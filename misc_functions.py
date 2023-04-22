######################################################################################
def print_header(codename,mode="Sergio"):
    """Print code header"""
    if (mode in ["Sergio"]):
        len_target = 70
        sepline = ""
        while len(sepline) < len_target:
            sepline = sepline + "#"
        head_print = (
            "\n" + sepline + "\n" + codename.center(len_target) + "\n" + sepline + "\n"
        )
    else:
        head_print = ":> "+codename.center(30)+"\n"
    print(head_print)
    return

######################################################################################
# This function generates the snapshot ID text
# (default to RAMSES length)
def read_name_funct(i, ndigits=5):
    ID = str(i)
    while len(ID) < ndigits:
        ID = "0" + ID
    return ID
######################################################################################

