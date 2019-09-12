import sharppy.databases.sars_cal as sars_cal

def test_sars_hail():
    results = sars_cal.check_hail_cal()
    verif = sars_cal.calc_verification(results)
    # Ensure every sounding listed in the database matches back to itself
    assert verif['num'] == verif['match']

def test_sars_supercell():
    results = sars_cal.check_supercell_cal()
    verif = sars_cal.calc_verification(results)
    # Ensure every sounding listed in the database matches back to itself
    assert verif['num'] == verif['match']

#test_sars_hail()
