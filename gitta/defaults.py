"""Build-time defaults.

CLIENT_ID is the public Client ID of the GitHub OAuth App that Gitta logs in
through (device flow). It is NOT a secret. Paste it here before building the
exe, so that the end user never has to see it. If it is empty, Gitta shows a
setup screen where it can be entered once.
"""

CLIENT_ID = ""
