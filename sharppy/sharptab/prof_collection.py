
import sharppy.sharptab.profile as profile

from multiprocessing import Process, Queue

class ProfCollection(object):
    def __init__(self, profiles, dates, target_type=profile.ConvectiveProfile, **kwargs):
        self._profs = profiles
        self._dates = dates
        self._meta = kwargs
        self._target_type = target_type
        self._highlight = profiles.keys()[0]
        self._prof_idx = 0
        self._analog_date = None

        self._mod_therm = [ False for d in self._dates ]
        self._mod_wind = [ False for d in self._dates ]

        self._orig_profs = {}
        self._async = None
        self._cancel_copy = False
        self._procs = []

    def subset(self, idxs):
        profiles = dict( (mem, [ prof[idx] for idx in idxs ]) for mem, prof in self._profs.iteritems() )
        dates = [ self._dates[idx] for idx in idxs ]
        return ProfCollection(profiles, dates, highlight=self._highlight, **self._meta)

    def _backgroundCopy(self, member, max_procs=2):
        def doCopy(target_type, prof, idx, pipe):
            pipe.put((target_type.copy(prof), idx))

        pipe = Queue(max_procs)

        for idx, prof in enumerate(self._profs[member]):
            proc = Process(target=doCopy, args=(self._target_type, prof, idx, pipe))
            proc.start()

            self._procs.append(proc)

            if (idx % max_procs) == 0 or idx == len(self._profs[member]) - 1:
                for proc in self._procs:
                    proc.join()

                    prof, copy_idx  = pipe.get()
                    self._profs[member][copy_idx] = prof

                self._procs = []
        return

    def setAsync(self, async):
        self._async = async
        self._async.post(self._backgroundCopy, None, self._highlight)

    def cancelCopy(self):
        for proc in self._procs:
            proc.terminate()
        if self._async is not None:
            self._async.clearQueue()

    def getMeta(self, key, index=False):
        meta = self._meta[key]
        if index:
            meta = meta[self._prof_idx]
        return meta

    def getCurrentDate(self):
        if not self.hasCurrentProf():
            return

        return self._dates[self._prof_idx]

    def getHighlightedProf(self):
        if not self.hasCurrentProf():
            return

        cur_prof = self._profs[self._highlight][self._prof_idx]
        if type(cur_prof) != profile.ConvectiveProfile:
            self._profs[self._highlight][self._prof_idx] = self._target_type.copy(cur_prof)
        return self._profs[self._highlight][self._prof_idx]

    def getCurrentProfs(self):
        if not self.hasCurrentProf():
            return {}

        for mem, profs in self._profs.iteritems():
            # Copy the profiles on the fly
            cur_prof = profs[self._prof_idx]

            if mem == self._highlight and type(cur_prof) != self._target_type:
                self._profs[mem][self._prof_idx] = self._target_type.copy(cur_prof)
            elif type(cur_prof) not in [ profile.BasicProfile, self._target_type ]:
                self._profs[mem][self._prof_idx] = profile.BasicProfile.copy(cur_prof)

        profs = dict( (mem, profs[self._prof_idx]) for mem, profs in self._profs.iteritems() ) 
        return profs

    def getAnalogDate(self):
        return self._analog_date

    def isModified(self):
        if not self.hasCurrentProf():
            return False
        return self._mod_therm[self._prof_idx] or self._mod_wind[self._prof_idx]

    def isEnsemble(self):
        return len(self._profs.keys()) > 1

    def hasCurrentProf(self):
        return self._prof_idx >= 0

    def hasMeta(self, key):
        return key in self._meta

    def setMeta(self, key, value):
        self._meta[key] = value

    def setHighlightedMember(self, member_name):
        self._highlight = member_name

    def setCurrentDate(self, cur_dt):
        try:
            self._prof_idx = self._dates.index(cur_dt)
        except ValueError:
            self._prof_idx = -1

    def setAnalogToDate(self, analog_to_date):
        self._analog_date = self._dates[0]
        self._dates = [ analog_to_date ]

    def advanceTime(self, direction):
        length = len(self._dates)
        if direction > 0 and self._prof_idx == length - 1:
            self._prof_idx = 0
        elif direction < 0 and self._prof_idx == 0:
            self._prof_idx = length - 1
        else:
            self._prof_idx += direction
        return self._dates[self._prof_idx]

    def advanceHighlight(self, direction):
        mem_names = sorted(self._profs.keys())
        high_idx = mem_names.index(self._highlight)
        length = len(mem_names)

        if direction > 0 and high_idx == length - 1:
            adv_idx = 0
        if direction < 0 and high_idx == 0:
            adv_idx = length - 1
        else:
            adv_idx = high_idx + direction

        self._highlight = mem_names[adv_idx]

    def defineUserParcel(self, parcel):
        if self.hasCurrentProf():
            self._profs[self._highlight][self._prof_idx].usrpcl = parcel

    def modify(self, idx, **kwargs):
        if self.isEnsemble():
            raise ValueError("Can't modify ensemble profiles")

        prof = self._profs[self._highlight][self._prof_idx]

        # Save original, if one hasn't already been saved
        if self._prof_idx not in self._orig_profs:
            self._orig_profs[self._prof_idx] = prof

        cls = type(prof)
        # Copy the variables to be modified
        prof_vars = dict( (k, prof.__dict__[k].copy()) for k in kwargs.iterkeys() )

        # Do the modification
        for var, val in kwargs.iteritems():
            prof_vars[var][idx] = val

        # Make a copy of the profile object with the newly modified variables inserted.
        
        self._profs[self._highlight][self._prof_idx] = cls.copy(prof, **prof_vars)

        # Update bookkeeping
        if 'tmpc' in kwargs or 'dwpc' in kwargs:
            self._mod_therm[self._prof_idx] = True

        if 'u' in kwargs or 'v' in kwargs or 'wdir' in kwargs or 'wspd' in kwargs:
            self._mod_wind[self._prof_idx] = True

    def reset(self, *args):
        if not self._prof_idx in self._orig_profs:
            return

        prof = self._orig_profs[self._prof_idx]
        cls = type(prof)

        # Get the original variables
        prof_vars = dict( (k, prof.__dict__[k]) for k in args )

        # Make a copy of the profile object with the original variables inserted
        self._profs[self._highlight][self._prof_idx] = cls.copy(prof, **prof_vars)

        # Update bookkeeping
        if 'tmpc' in args or 'dwpc' in args:
            self._mod_therm[self._prof_idx] = False

        if 'u' in args or 'v' in args or 'wdir' in args or 'wspd' in args:
            self._mod_wind[self._prof_idx] = False

        if not self.isModified():
            del self._orig_profs[self._prof_idx]
