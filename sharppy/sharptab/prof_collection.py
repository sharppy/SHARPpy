
from __future__ import absolute_import

import sharppy.sharptab.profile as profile
import sharppy.sharptab.interp as interp
from utils.frozenutils import Process, Queue
import platform
import numpy as np

def doCopy(target_type, prof, idx, pipe):
    pipe.put((target_type.copy(prof), idx))
    
class ProfCollection(object):
    """
    ProfCollection: A class to keep track of profiles from a single data source. Handles time switching, ensemble member switching,
        and modifications to profiles.
    """
    def __init__(self, profiles, dates, target_type=profile.ConvectiveProfile, **kwargs):
        """
        Initialize the collection.
        profiles:   A dictionary of lists of profiles.  The keys of the dictionary are the ensemble member names, the
            values are lists of profiles for those members over time.
        dates:      A list of datetime objects corresponding to the times for each element of the lists in profiles.
        target_type:    The type to copy the profiles to when requested. Default is a ConvectiveProfile.
        **kwargs:   Metadata for the profile.
        """
        self._profs = profiles
        self._dates = dates
        self._meta = kwargs
        self._target_type = target_type
        self._highlight = kwargs.get('highlight', list(profiles.keys())[0])
        self._prof_idx = 0
        self._analog_date = None

        self._mod_therm = [ False for d in self._dates ]
        self._mod_wind = [ False for d in self._dates ]
        self._interp = [ False for d in self._dates ]

        self._orig_profs = {}
        self._interp_profs = {}
        self._async = None
        self._cancel_copy = False
        self._procs = []

    def subset(self, idxs):
        """
        Subset the profile collection over time.
        idxs:   The time indices to include in the subsetted collection.
        """
        def extract_profile_indexes(prof):
            prof_indexed = []
            for idx in idxs:
                try:
                    prof_indexed.append(prof[idx])
                except IndexError:
                    pass

            return prof_indexed

        profiles = dict( (mem, extract_profile_indexes(prof)) for mem, prof in self._profs.items() )
        dates = [ self._dates[idx] for idx in idxs ]
        return ProfCollection(profiles, dates, highlight=self._highlight, **self._meta)

    def _backgroundCopy(self, member, max_procs=2):
        """
        Copies the profile objects in the background while the user can continue to do things.
        This upgrades the project object types from Profile to ConvectiveProfile via the
        _target_type variable.
        
        member:     the key indicating a specific member
        max_procs:  max number of processors to perform this action
        """
        pipe = Queue(max_procs)

        for idx, prof in enumerate(self._profs[member]):
            proc = Process(target=doCopy, args=(self._target_type, prof, idx, pipe))
            proc.start()

            self._procs.append(proc)
            
            if (idx % max_procs) == 0 or idx == len(self._profs[member]) - 1:
                for proc in self._procs:

                    if platform.system() != "Windows":
                        # Windows hangs here for some reason, but runs fine without it.
                        proc.join()
                        
                    prof, copy_idx  = pipe.get()
                    self._profs[member][copy_idx] = prof
                    
                self._procs = []
        return

    def setAsync(self, async_obj):
        """
        Start an asynchronous process to load objects of type 'target_type' in the background.
        Used to upgrade the Profile objects to ConvectiveProfile objects in the background

        async:  An AsyncThreads instance.
        """
        self._async = async_obj
        self._async.post(self._backgroundCopy, None, self._highlight)

    def cancelCopy(self):
        """
        Terminates any threads that are running in the background.
        """
        for proc in self._procs:
            proc.terminate()
        if self._async is not None:
            self._async.clearQueue()

    def getMeta(self, key, index=False):
        """
        Returns metadata about the profile.
        key:    What metadata to return.
        index [optional]: If true, treat the metadata as an array with the same length as dates passed in the constructor.
            Returns value of that array at this time index..
        """
        meta = self._meta[key]
        if index:
            meta = meta[self._prof_idx]
        return meta

    def getCurrentDate(self):
        """
        Returns the current date in the profile object
        """
        if not self.hasCurrentProf():
            return

        return self._dates[self._prof_idx]

    def getHighlightedProf(self):
        """
        Returns which profile is highlighted.
        """
        if not self.hasCurrentProf():
            return

        cur_prof = self._profs[self._highlight][self._prof_idx]
        # If the currently selected profile is not of the target_type (e.g., ConvectiveProfile), then
        # then upgrade it via the copy function.
        if type(cur_prof) != self._target_type:
            self._profs[self._highlight][self._prof_idx] = self._target_type.copy(cur_prof)
        return self._profs[self._highlight][self._prof_idx]

    def getCurrentProfs(self):
        """
        Returns the profiles at the current time.
        """
        if not self.hasCurrentProf():
            return {}

        for mem, profs in self._profs.items():
            # Copy the profiles on the fly
            try:
                cur_prof = profs[self._prof_idx]
            except IndexError:
                continue
            else:
                if mem == self._highlight and type(cur_prof) != self._target_type:
                    self._profs[mem][self._prof_idx] = self._target_type.copy(cur_prof)
                elif type(cur_prof) not in [ profile.BasicProfile, self._target_type ]:
                    self._profs[mem][self._prof_idx] = profile.BasicProfile.copy(cur_prof)

        profs = dict( (mem, profs[self._prof_idx]) for mem, profs in self._profs.items() if len(profs) > self._prof_idx ) 
        return profs

    def getAnalogDate(self):
        """
        If this is an analog, return the date of the analog. Otherwise, returns None.
        """
        return self._analog_date

    def isModified(self):
        """
        Returns True if the profiles at the current time have been modified.  Returns False otherwise.
        """
        if not self.hasCurrentProf():
            return False
        return self._mod_therm[self._prof_idx] or self._mod_wind[self._prof_idx]

    def isInterpolated(self):
        """
        Returns True if the profiles at the current time have been modified.  Returns False otherwise.
        """
        if not self.hasCurrentProf():
            return False
        return self._interp[self._prof_idx]

    def isEnsemble(self):
        """
        Returns True if this collection has multiple ensemble members. Otherwise, returns False.
        """
        return len(list(self._profs.keys())) > 1

    def hasCurrentProf(self):
        """
        Returns True if the collection has a profile at the current time. Otherwise, returns False.
        """
        return self._prof_idx >= 0

    def hasMeta(self, key):
        """
        Returns True if the collection has metadata corresponding to 'key'. Otherwise returns False.
        """
        return key in self._meta

    def setMeta(self, key, value):
        """
        Sets the metadata 'key' to 'value'.
        """
        self._meta[key] = value

    def setHighlightedMember(self, member_name):
        """
        Sets the highlighted ensemble member to be 'member_name'.
        """
        self._highlight = member_name

    def getHighlightedMemberName(self):
        """
        Gets the name of the member that is currently highlighted.
        """
        return self._highlight

    def setCurrentDate(self, cur_dt):
        """
        Sets the current date to be 'cur_dt'.
        cur_dt:     A datetime object specifiying which date to set it to.
        """
        try:
            self._prof_idx = self._dates.index(cur_dt)
        except ValueError:
            pass

    def setAnalogToDate(self, analog_to_date):
        """
        Specify that this collection represents an analog; the date is set to 'analog_to_date', and the 
            analog date is set to the former date.
        analog_to_date: A datetime object that specifies the date to which this collection is an analog.
        """
        self._analog_date = self._dates[0]
        self._dates = [ analog_to_date ]

    def advanceTime(self, direction):
        """
        Advance time in a direction specified by 'direction'. Returns a datetime object containing the new time.
        direction:  An integer (ether 1 or -1) specifying which direction to move time in. 1 moves time forward,
            -1 moves time backward.
        """
        length = len(self._dates)
        if direction > 0 and self._prof_idx == length - 1:
            self._prof_idx = 0
        elif direction < 0 and self._prof_idx == 0:
            self._prof_idx = length - 1
        else:
            self._prof_idx += direction
        return self._dates[self._prof_idx]

    def advanceHighlight(self, direction):
        """
        Change which member is highlighted.
        direction:  An integer (either 1 or -1) specifying which direction to go in the list. The list is in
            alphabetical order, so the members will be gone through in that order. 
        """
        mem_names = sorted(self._profs.keys())
        high_idx = mem_names.index(self._highlight)
        length = len(mem_names)
        
        def doAdvance(adv_idx):
            if direction > 0 and adv_idx == length - 1:
                adv_idx = 0
            elif direction < 0 and adv_idx == 0:
                adv_idx = length - 1
            else:
                adv_idx = adv_idx + direction
            return adv_idx

        adv_idx = doAdvance(high_idx)
        highlight = mem_names[adv_idx]
        while len(self._profs[highlight]) <= self._prof_idx:
            adv_idx = doAdvance(adv_idx)
            highlight = mem_names[adv_idx]
        self._highlight = highlight

    def defineUserParcel(self, parcel):
        """
        Defines a custom parcel for the current profile.
        parcel:     A parcel object to use as the custom parcel.
        """
        if self.hasCurrentProf():
            self._profs[self._highlight][self._prof_idx].usrpcl = parcel

    def modify(self, idx, **kwargs):
        """
        Modify the profile at the current time.
        idx:    The vertical index to modify
        **kwargs:   The variables to modify ('tmpc', 'dwpc', 'u', or 'v')
        
        TODO: Allow modification of layers.  Could be that idx is -999 for layer
              and kwargs passes information about the layers to be modified.
        """
        if self.isEnsemble():
            raise ValueError("Can't modify ensemble profiles")

        prof = self._profs[self._highlight][self._prof_idx]

        # Save original, if one hasn't already been saved
        if self._prof_idx not in self._orig_profs:
            self._orig_profs[self._prof_idx] = prof

        cls = type(prof)
        # Copy the variables to be modified
        prof_vars = dict( (k, prof.__dict__[k].copy()) for k in kwargs.keys() if k != 'idx_range')
        
        if idx != -999:
            # Do the modification
            for var, val in kwargs.items():
                prof_vars[var][idx] = val
        else:
            idx = kwargs.get('idx_range')
            for key in prof_vars.keys():
                prof_vars[key] = kwargs.get(key)
 
        # Make a copy of the profile object with the newly modified variables inserted.
        self._profs[self._highlight][self._prof_idx] = cls.copy(prof, **prof_vars)

        # Update bookkeeping
        if 'tmpc' in kwargs or 'dwpc' in kwargs:
            self._mod_therm[self._prof_idx] = True

        if 'u' in kwargs or 'v' in kwargs or 'wdir' in kwargs or 'wspd' in kwargs:
            self._mod_wind[self._prof_idx] = True

    def modifyStormMotion(self, deviant, vec_u, vec_v):
        if deviant == 'left':
            self._profs[self._highlight][self._prof_idx].set_srleft(vec_u, vec_v)
        elif deviant == 'right':
            self._profs[self._highlight][self._prof_idx].set_srright(vec_u, vec_v)

    def resetStormMotion(self):
        self._profs[self._highlight][self._prof_idx].reset_srm()

    def interp(self, dp=-25):
        """
        Interpolate the profile object to a specific pressure level spacing.
        """

        if self.isEnsemble():
            raise ValueError("Cannot interpolate the ensemble profiles.")

        prof = self._profs[self._highlight][self._prof_idx]

        # Save original, if one hasn't already been saved
        if self._prof_idx not in self._orig_profs:
            self._orig_profs[self._prof_idx] = prof

        cls = type(prof)
        # Copy the tmpc, dwpc, etc. profiles to be inteprolated
        keys = ['tmpc', 'dwpc', 'hght', 'wspd', 'wdir', 'omeg']
        
        prof_vars = {'pres': np.arange(prof.pres[prof.sfc], prof.pres[prof.top], dp)}
        prof_vars['tmpc'] = interp.temp(prof, prof_vars['pres'])
        prof_vars['dwpc'] = interp.dwpt(prof, prof_vars['pres'])
        prof_vars['hght'] = interp.hght(prof, prof_vars['pres'])
        if prof.omeg.all() is not np.ma.masked:
            prof_vars['omeg'] = interp.omeg(prof, prof_vars['pres'])
        else:
            prof_vars['omeg'] = np.ma.masked_array(prof_vars['pres'], mask=np.ones(len(prof_vars['pres']), dtype=int))
        u, v = interp.components(prof, prof_vars['pres'])
        prof_vars['u'] = u
        prof_vars['v'] = v

        interp_prof = cls.copy(prof, **prof_vars)
        self._profs[self._highlight][self._prof_idx] = interp_prof

         # Save the original like in modify()
        if self._prof_idx not in self._interp_profs:
            self._interp_profs[self._prof_idx] = interp_prof
       
        # Update bookkeeping
        self._interp[self._prof_idx] = True

    def resetModification(self, *args):
        """
        Reset the profile to its original state.
        *args:  The variables to reset ('tmpc', 'dwpc', 'u', or 'v').
        """
        if not self._prof_idx in self._orig_profs:
            return

        if self._interp[self._prof_idx]:
            orig_prof = self._interp_profs[self._prof_idx]
        else:
            orig_prof = self._orig_profs[self._prof_idx]

        prof = self._profs[self._highlight][self._prof_idx]
        cls = type(prof)

        # Get the original variables
        prof_vars = dict( (k, orig_prof.__dict__[k]) for k in args )

        # Make a copy of the profile object with the original variables inserted
        self._profs[self._highlight][self._prof_idx] = cls.copy(prof, **prof_vars)

        # Update bookkeeping
        if 'tmpc' in args or 'dwpc' in args:
            self._mod_therm[self._prof_idx] = False

        if 'u' in args or 'v' in args or 'wdir' in args or 'wspd' in args:
            self._mod_wind[self._prof_idx] = False

        if not self.isModified() and not self.isInterpolated():
            del self._orig_profs[self._prof_idx]

    def resetInterpolation(self):
        if not self._prof_idx in self._interp_profs:
            return

        self._profs[self._highlight][self._prof_idx] = self._orig_profs[self._prof_idx]

        prof = self._profs[self._highlight][self._prof_idx]
#       print dict( (k, prof.__dict__[k].shape[0]) for k in [ 'pres', 'hght', 'tmpc', 'dwpc', 'u', 'v' ])

        del self._orig_profs[self._prof_idx]
        del self._interp_profs[self._prof_idx]

        self._mod_wind[self._prof_idx] = False
        self._mod_therm[self._prof_idx] = False
        self._interp[self._prof_idx] = False
