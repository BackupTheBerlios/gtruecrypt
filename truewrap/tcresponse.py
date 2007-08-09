# truecryptresponse from "forcefield" [ http://bockcay.de/forcefield ]


import re
ENTER_PASSWORD= "Enter password.*\'.*\'"
ENTER_HIDDEN_PASSWORD= "Enter hidden volume password.*"
ENTER_PASSWORD_43A= "Enter.*or.*system password:"
REENTER_PASSWORD= "Re-enter.*"
ENTER_KEYFILES= "Enter keyfile path.*"
ENTER_HIDDEN_KEYFILES= "Enter keyfile path for hidden volume.*"
ENTER_PROTECTION= "Protect hidden volume?.*" #TODO
ENTER_VOLUME= "Enter volume path:.*"
ENTER_MOUNTPATH= ".*Enter mount.*"
ADMIN_RIGHTS_REQUIRED= ".*Administrator.*root.*privileges.*"

MOUNTING_SUCCESSFULL = "Mapped.*as.*\n.*Mounted.*at.*"
DISMOUNTING_SUCCESSFULL = ".*not mounted*"

INCORRECT_VOLUME= ".*Incorrect password or not a TrueCrypt volume.*"
NOT_A_DIRECTORY= ".*Cannot open file or device: Not a directory.*"
VOLUME_CREATED = ".*created.*" #TODO
VOLUME_MOUNTED = ".*mounted.*" #TODO
VOLUME_EXISTS  = "Volume already exists - overwrite.*" #TODO

PLEASE_TYPE = ".*Please type at least 320 randomly chosen characters and then press Enter.*"

EOF = "EOF"
PROGRESS_RANDOM = ".*(?P<percent> [0-9]+%)"
PROGRESS_REGEXP = re.compile(PROGRESS_RANDOM)

CREATE_PROGRESS = "\rDone: (?P<size>[0-9]*\.[0-9]*) (?P<size_unit>[GBKM]{2}).*[0-5][0-9]  "
CREATE_PROGRESS_REGEXP = re.compile(CREATE_PROGRESS)

CREATED_PATTERN= ".*Volume created.*"
CREATEDREGEXP= re.compile(CREATED_PATTERN)

MOUSE_CONNECTED = "Is your mouse connected directly to computer where TrueCrypt is running?.*"

ALREADY_MAPPED = ".*Volume already mapped.*"
CANNOT_OPEN_VOLUME = '.*Cannot open volume.*'
NO_VOLUMES_MAPPED = ".*No volumes mapped.*"

ENTER_SUDO_PASSWORD = "Password:.*"
NOT_SUDO = " ^((?!Password).)*$ "

SUDO_TEST= "sudotest"
SUDO_WRONG_PASSWORD= "Sorry, try again"

KEYFILE_DOES_NOT_EXIST = ".*truecrypt: Error while processing keyfiles.*"


LISTPATTERN= "/.*dev.*mapper.*"

ANYTHING = ".*"
ENTER = "Enter.*"
TRUECRYPT= "truecrypt.*"

PROPERTIES= ".*Volume properties.*"
ILLEGAL_SEEK= ".*Illegal seek.*"
TIMEOUT_TEST= "timeout_test.*"

MOUNT_POINT_DOES_NOT_EXIST= ".*mount: mount point.*does not exist.*"
DEVICE_BUSY = ".*device is busy.*"
OUTER_VOLUME_TOO_SMALL = "Outer volume too small for the size specified.*"
WRONG_FS_TYPE = "mount: wrong fs type.*"
SUDO_PASSWORD = "[sudo].*password for.*"
REVERSED_PATCH_DETECTED = ".*Reversed (or previously applied) patch detected!.*"
TRY_AGAIN = "Sorry, try again."
CANCELED = "canceled"
