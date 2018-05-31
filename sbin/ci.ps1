[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)

# TODO: Bootstrap the bootstrapper. See appveyor.ps1.
$global:UnitTestingPowerShellScriptsDirectory = $env:TEMP

# Scripts other than the bootstrapper are located here.
$global:UnitTestingPowerShellScriptsDirectory = $env:TEMP

if (!$env:UNITTESTING_BOOTSTRAPPED) {
    write-output "[UnitTesting] bootstrapping environment..."

    # UTF8 encoding without preamble.
    $local:utf8 = [System.Text.UTF8Encoding]::new($false)

    # Files encoded in base64 encoding. They need to be unpacked before they can be used.
    # !!! Every time they change, they need to be regenerated and copied here. !!!
    $local:encodedDependencies = @(
'utils.ps1@@@QWRkLVR5cGUgLUFzc2VtYmx5TmFtZSBTeXN0ZW0uSU8uQ29tcHJlc3Npb24uRmlsZVN5
c3RlbQoKZnVuY3Rpb24gZW5zdXJlQ3JlYXRlRGlyZWN0b3J5IHsKICAgIHBhcmFtKFtzdHJpbmddJFBh
dGgpCiAgICBbdm9pZF0obmV3LWl0ZW0gLWl0ZW10eXBlIGQgIiRQYXRoIiAtZm9yY2UgLWVycm9yYWN0
aW9uIHN0b3ApCn0KCmZ1bmN0aW9uIGVpdGhlck9yIHsKICAgIHBhcmFtKCRMZWZ0LCAkUmlnaHQpCiAg
ICBpZiAoJExlZnQpIHsgJExlZnQgfSBlbHNlIHsgJFJpZ2h0IH0KfQoKZnVuY3Rpb24gbnVsbE9yIHsK
ICAgIHBhcmFtKCRMZWZ0LCAkUmlnaHQpCiAgICBpZiAoJExlZnQgLWVxICRudWxsKSB7ICRMZWZ0IH0g
ZWxzZSB7ICRSaWdodCB9Cn0KCmZ1bmN0aW9uIHRvTG9nTWVzc2FnZSB7CiAgICBwYXJhbShbc3RyaW5n
XSRjb250ZW50KQogICAgIltVbml0VGVzdGluZ10gJGNvbnRlbnQiCn0KCmZpbHRlciBsb2dWZXJib3Nl
IHsKICAgIHBhcmFtKFtzdHJpbmddJG1lc3NhZ2UpCiAgICB3cml0ZS12ZXJib3NlICh0b0xvZ01lc3Nh
Z2UgKGVpdGhlck9yICRfICRtZXNzYWdlKSkKfQoKZmlsdGVyIGxvZ1dhcm5pbmcgewogICAgcGFyYW0o
W3N0cmluZ10kbWVzc2FnZSkKICAgIHdyaXRlLXdhcm5pbmcgKHRvTG9nTWVzc2FnZSAoZWl0aGVyT3Ig
JF8gJG1lc3NhZ2UpKQp9CgpmaWx0ZXIgbG9nRXJyb3IgewogICAgcGFyYW0oW3N0cmluZ10kbWVzc2Fn
ZSkKICAgIHdyaXRlLWVycm9yICh0b0xvZ01lc3NhZ2UgKGVpdGhlck9yICRfICRtZXNzYWdlKSkKfQoK
ZnVuY3Rpb24gZW5zdXJlQ29weURpcmVjdG9yeUNvbnRlbnRzIHsKICAgIHBhcmFtKFtzdHJpbmddJFBh
dGgsIFtzdHJpbmddJERlc3RpbmF0aW9uKQogICAgY29weS1pdGVtICIkUGF0aFwqIiAtcmVjdXJzZSAt
Zm9yY2UgJERlc3RpbmF0aW9uIC1lcnJvcmFjdGlvbiBzdG9wCn0KCmZ1bmN0aW9uIGVuc3VyZVJlbW92
ZURpcmVjdG9yeSB7CiAgICBwYXJhbShbc3RyaW5nXSRQYXRoKQogICAgaWYgKFtTeXN0ZW0uSU8uUGF0
aC5GaWxlXS5FeGlzdHMoKGNvbnZlcnQtcGF0aCAkUGF0aCkpKSB7CiAgICAgICAgdGhyb3cgImV4cGVj
dGVkIGEgZGlyZWN0b3J5LCBnb3QgYSBmaWxlOiAkUGF0aCIKICAgIH0KICAgIHJlbW92ZS1pdGVtICIk
UGF0aCIgLXJlY3Vyc2UgLWZvcmNlIC1lcnJvcmFjdGlvbiBzdG9wCn0KCmZ1bmN0aW9uIGdpdEZldGNo
TGF0ZXN0VGFnRnJvbVJlcG9zaXRvcnkgewogICAgcGFyYW0oW3N0cmluZ10kVXJsVG9SZXBvc2l0b3J5
KQogICAgZ2l0IGxzLXJlbW90ZSAtLXRhZ3MgIiRVcmxUb1JlcG9zaXRvcnkiIHwgJXskXyAtcmVwbGFj
ZSAiLiovKC4qKSQiLCAnJDEnfSBgCiAgICAgICAgfCB3aGVyZS1vYmplY3QgeyRfIC1ub3RtYXRjaCAi
XF4ifSB8JXtbU3lzdGVtLlZlcnNpb25dJF99IGAKICAgICAgICB8IHNvcnQgfCBzZWxlY3Qtb2JqZWN0
IC1sYXN0IDEgfCAleyAiJF8iIH0KfQoKZnVuY3Rpb24gZ2l0Q2xvbmVUYWcgewogICAgcGFyYW0oW3N0
cmluZ10kVGFnLCBbc3RyaW5nXSRSZXBvc2l0b3J5VXJsLCBbc3RyaW5nXSREZXN0aW5hdGlvbikKICAg
IGdpdCBjbG9uZSAtLXF1aWV0IC0tZGVwdGggMSAtLWJyYW5jaD0kVGFnICRSZXBvc2l0b3J5VXJsICIk
RGVzdGluYXRpb24iIDI+JG51bGwKfQoKZnVuY3Rpb24gZ2l0R2V0SGVhZFJldmlzaW9uTmFtZSB7CiAg
ICBwYXJhbShbc3RyaW5nXSRSZXBvc2l0b3J5RGlyZWN0b3J5KQogICAgZ2l0IC1DICRSZXBvc2l0b3J5
RGlyZWN0b3J5IHJldi1wYXJzZSBIRUFECn0KCmZ1bmN0aW9uIGdldExhdGVzdFVuaXRUZXN0aW5nQnVp
bGRUYWcgewogICAgcGFyYW0oW3N0cmluZ10kVGFnLCBbc3RyaW5nXSRTdWJsaW1lVGV4dFZlcnNpb24s
IFtzdHJpbmddJFVybFRvVW5pdFRlc3RpbmcpCiAgICAkcmVzdWx0ID0gJFRhZwogICAgaWYgKFtzdHJp
bmddOjpJc051bGxPckVtcHR5KCRUYWcpKXsKICAgICAgICBpZiAoJFN1YmxpbWVUZXh0VmVyc2lvbiAt
ZXEgMikgewogICAgICAgICAgICAkcmVzdWx0ID0gJzAuMTAuNicKICAgICAgICB9IGVsc2VpZiAoJFN1
YmxpbWVUZXh0VmVyc2lvbiAtZXEgMykgewogICAgICAgICAgICAkcmVzdWx0ID0gZ2l0RmV0Y2hMYXRl
c3RUYWdGcm9tUmVwb3NpdG9yeSAkVXJsVG9Vbml0VGVzdGluZwogICAgICAgIH0KICAgIH0KICAgICRy
ZXN1bHQKfQoKZnVuY3Rpb24gZ2V0UmVwb3NpdG9yeVRhZyB7CiAgICBwYXJhbShbc3RyaW5nXSRQcmVm
ZXJyZWRUYWcsIFtzdHJpbmddJFJlcG9zaXRvcnlVcmwpCiAgICBpZiAoW3N0cmluZ106OklzTnVsbE9y
RW1wdHkoJFByZWZlcnJlZFRhZykpIHsgZ2l0RmV0Y2hMYXRlc3RUYWdGcm9tUmVwb3NpdG9yeSAkUmVw
b3NpdG9yeVVybCB9CiAgICBlbHNlIHsgJFByZWZlcnJlZFRhZyB9Cn0KCmZ1bmN0aW9uIGNsb25lUmVw
b3NpdG9yeVRhZyB7CiAgICBwYXJhbShbc3RyaW5nXSRQcmVmZXJyZWRUYWcsIFtzdHJpbmddJFJlcG9z
aXRvcnlVcmwsIFtzdHJpbmddJERlc3RpbmF0aW9uKQogICAgJFRhZyA9IGdldFJlcG9zaXRvcnlUYWcg
JFByZWZlcnJlZFRhZyAkUmVwb3NpdG9yeVVybAogICAgbG9nVmVyYm9zZSAiY2xvbmluZyAkKHNwbGl0
LXBhdGggJFJlcG9zaXRvcnlVcmwgLWxlYWYpIHRhZzogJFRhZyBpbnRvICREZXN0aW5hdGlvbi4uLiIK
ICAgIGdpdENsb25lVGFnICRUYWcgJFJlcG9zaXRvcnlVcmwgJERlc3RpbmF0aW9uCiAgICBnaXRHZXRI
ZWFkUmV2aXNpb25OYW1lICREZXN0aW5hdGlvbiB8IGxvZ1ZlcmJvc2UKICAgIGxvZ1ZlcmJvc2UgIiIK
fQoKZnVuY3Rpb24gZ2V0TGF0ZXN0Q29sb3JTY2hlbWVVbml0VGFnIHsKICAgIHBhcmFtKFtzdHJpbmdd
JFRhZywgW3N0cmluZ10kVXJsVG9Db2xvclNjaGVtZVVuaXQpCiAgICBpZiAoW3N0cmluZ106OklzTnVs
bE9yRW1wdHkoJFRhZykpIHsgZ2l0RmV0Y2hMYXRlc3RUYWdGcm9tUmVwb3NpdG9yeSAkVXJsVG9Db2xv
clNjaGVtZVVuaXQgfQogICAgZWxzZSB7ICRUYWcgfQp9CgpmdW5jdGlvbiBlbnN1cmVDcmVhdGVEaXJl
Y3RvcnlKdW5jdGlvbiB7CiAgICBwYXJhbShbc3RyaW5nXSRMaW5rLCBbc3RyaW5nXSRUYXJnZXQpCiAg
ICBjbWQuZXhlIC9jIG1rbGluayAvSiAiJExpbmsiICIkVGFyZ2V0IgogICAgaWYgKCRMQVNURVhJVENP
REUgLW5lIDApIHsgdGhyb3cgImNvdWxkIG5vdCBjcmVhdGUgZGlyZWN0b3J5IGp1bmN0aW9uIGF0ICRM
aW5rIHRvICRUYXJnZXQiIH0KfQoKZnVuY3Rpb24gZW5zdXJlVmFsdWUgewogICAgcGFyYW0oJFZhbHVl
LCBbc3RyaW5nXSRQYXR0ZXJuPSdeLiokJywgW3N0cmluZ10kTWVzc2FnZT0kbnVsbCkKICAgIGlmKCgk
VmFsdWUgLWVxICRudWxsKSAtb3IgKCRWYWx1ZSAtbm90bWF0Y2ggJFBhdHRlcm4pKSB7CiAgICAgICAg
dGhyb3cgKGVpdGhlck9yICRNZXNzYWdlICJ2YWx1ZSBpcyBudWxsIG9yIHVuZXhwZWN0ZWQgKGV4cGVj
dGVkIG1hdGNoOiAkUGF0dGVybjsgZ290OiAkVmFsdWUpIikKICAgIH0KICAgICRWYWx1ZQp9CgpmdW5j
dGlvbiBwYXRoRXhpc3RzIHsKICAgIHBhcmFtKFtzdHJpbmddJFBhdGgsIFtzd2l0Y2hdJE5lZ2F0ZT0k
RmFsc2UpCiAgICBpZiAoISROZWdhdGUpIHsgdGVzdC1wYXRoICRQYXRoIH0gZWxzZSB7ICEodGVzdC1w
YXRoICRQYXRoKSB9Cn0KCmZ1bmN0aW9uIGluc3RhbGxQYWNrYWdlRm9yU3VibGltZVRleHRWZXJzaW9u
M0lmTm90UHJlc2VudCB7CiAgICBwYXJhbShbc3RyaW5nXSRQYXRoLCBbc3RyaW5nXSRQcmVmZXJyZWRU
YWcsIFtzdHJpbmddJFJlcG9zaXRvcnlVcmwpCiAgICBpZiAoJElzU3VibGltZVRleHRWZXJzaW9uMyAt
YW5kIChwYXRoRXhpc3RzIC1OZWdhdGUgJFBhdGgpKSB7CiAgICAgICAgY2xvbmVSZXBvc2l0b3J5VGFn
ICRQcmVmZXJyZWRUYWcgJFJlcG9zaXRvcnlVcmwgJFBhdGgKICAgIH0KfQoKZnVuY3Rpb24gaWlmIHsK
ICAgIHBhcmFtKFtzY3JpcHRibG9ja10kQ29uZGl0aW9uLCAkSWZUcnVlLCAkSWZGYWxzZSkKICAgIGlm
ICgmJENvbmRpdGlvbikgeyAkSWZUcnVlIH0gZWxzZSB7JElmRmFsc2UgfQp9CgpmdW5jdGlvbiB1bnpp
cCB7CiAgICBwYXJhbShbc3RyaW5nXSRTb3VyY2UsIFtzdHJpbmddJFRhcmdldCkKICAgIFtTeXN0ZW0u
SU8uQ29tcHJlc3Npb24uWmlwRmlsZV06OkV4dHJhY3RUb0RpcmVjdG9yeSgkU291cmNlLCAkVGFyZ2V0
KQp9',
'ci_config.ps1@@@LiAkUFNTY3JpcHRSb290XHV0aWxzLnBzMQoKIyBXZSBtdXN0IHNldCBjb25zdGFu
dHMgb25seSBvbmNlLgppZiAoISRlbnY6VU5JVFRFU1RJTkdfQk9PVFNUUkFQUEVEKSB7CiAgICBmdW5j
dGlvbiBsb2NhbDptYWtlR2xvYmFsQ29uc3RhbnQgewogICAgICAgIHBhcmFtKFtzdHJpbmddJE5hbWUs
ICRWYWx1ZSkKICAgICAgICBuZXctdmFyaWFibGUgLW5hbWUgJE5hbWUgLXZhbHVlICRWYWx1ZSAtb3B0
aW9uIGNvbnN0YW50IC1zY29wZSBnbG9iYWwKICAgIH0KCiAgICBsb2dWZXJib3NlICJzZXR0aW5nIGds
b2JhbCBjb25zdGFudHMgYW5kIHZhcmlhYmxlcy4uLiIKCiAgICAjIFRPRE86IElmIHdlIHVzZWQgZGly
ZWN0b3J5IGp1bmN0aW9ucyBoZXJlIHRvbywgd2Ugd291bGRuJ3QgbmVlZCB0aGlzPwogICAgIyBUaGlz
IGNvbnN0YW50IG1lYW5zIHRoYXQgdGhlIGVudGlyZSBjb250ZW50cyBvZiB0aGUgc291cmNlIGRpcmVj
dG9yeSBtdXN0IGJlIGNvcGllZCB0byB0aGUgdGFyZ2V0IGRpcmVjdG9yeS4KICAgIG1ha2VHbG9iYWxD
b25zdGFudCBTeW1ib2xDb3B5QWxsICdfX2FsbF9fJwoKCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgU3Vi
bGltZVRleHRWZXJzaW9uIChlbnN1cmVWYWx1ZSAkZW52OlNVQkxJTUVfVEVYVF9WRVJTSU9OICdeMnwz
JCcgLW1lc3NhZ2UgInRoZSBlbnZpcm9ubWVudCB2YXJpYWJsZSBTVUJMSU1FX1RFWFRfVkVSU0lPTiBt
dXN0IGJlIHNldCB0byAnMicgb3IgJzMnIikKICAgIG1ha2VHbG9iYWxDb25zdGFudCBJc1N1YmxpbWVU
ZXh0VmVyc2lvbjMgKCRTdWJsaW1lVGV4dFZlcnNpb24gLWVxIDMpCiAgICBtYWtlR2xvYmFsQ29uc3Rh
bnQgSXNTdWJsaW1lVGV4dFZlcnNpb24yICgkU3VibGltZVRleHRWZXJzaW9uIC1lcSAyKQogICAgbWFr
ZUdsb2JhbENvbnN0YW50IFN1YmxpbWVUZXh0RGlyZWN0b3J5IChlaXRoZXJPciAkZW52OlNVQkxJTUVf
VEVYVF9ESVJFQ1RPUlkgIkM6XHN0IikKICAgIG1ha2VHbG9iYWxDb25zdGFudCBTdWJsaW1lVGV4dEV4
ZWN1dGFibGVIZWxwZXJQYXRoIChqb2luLXBhdGggJFN1YmxpbWVUZXh0RGlyZWN0b3J5ICdzdWJsLmV4
ZScpCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgU3VibGltZVRleHRFeGVjdXRhYmxlUGF0aCAoam9pbi1w
YXRoICRTdWJsaW1lVGV4dERpcmVjdG9yeSAnc3VibGltZV90ZXh0LmV4ZScpCiAgICBtYWtlR2xvYmFs
Q29uc3RhbnQgU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAoZWl0aGVyT3IgJGVudjpTVUJMSU1F
X1RFWFRfUEFDS0FHRVNfRElSRUNUT1JZICJDOlxzdFxEYXRhXFBhY2thZ2VzIikKICAgIG1ha2VHbG9i
YWxDb25zdGFudCBTdWJsaW1lVGV4dFdlYnNpdGVVcmwgJ2h0dHBzOi8vd3d3LnN1YmxpbWV0ZXh0LmNv
bS8nCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgU3VibGltZVRleHRXZWJzaXRlVXJsRm9yVmVyc2lvbjMg
J2h0dHBzOi8vd3d3LnN1YmxpbWV0ZXh0LmNvbS8zJwogICAgbWFrZUdsb2JhbENvbnN0YW50IFN1Ymxp
bWVUZXh0V2Vic2l0ZVVybEZvclZlcnNpb24yICdodHRwczovL3d3dy5zdWJsaW1ldGV4dC5jb20vMicK
ICAgICAgICAjIFRPRE86IEZvciBjb21wYXRpYmlsaXR5OyByZW1vdmUgd2hlbiBub3QgdXNlZCBhbnlt
b3JlLgogICAgJGdsb2JhbDpTVFAgPSAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeQoKICAgIG1h
a2VHbG9iYWxDb25zdGFudCBQYWNrYWdlVW5kZXJUZXN0TmFtZSAoZW5zdXJlVmFsdWUgKGVpdGhlck9y
ICRlbnY6VU5JVFRFU1RJTkdfUEFDS0FHRV9VTkRFUl9URVNUX05BTUUgJGVudjpQQUNLQUdFKSAtbWVz
c2FnZSAidGhlIGVudmlyb25tZW50IHZhcmlhYmxlIFVOSVRURVNUSU5HX1BBQ0tBR0VfVU5ERVJfVEVT
VF9OQU1FIChvciBhbHRlcm5hdGl2ZWx5LCBQQUNLQUdFKSBpcyBub3Qgc2V0IikKICAgICMgVE9ETzog
Rm9yIGNvbXBhdGliaWxpdHk7IHJlbW92ZSB3aGVuIG5vdCB1c2VkIGFueW1vcmUuCiAgICBtYWtlR2xv
YmFsQ29uc3RhbnQgUGFja2FnZU5hbWUgJFBhY2thZ2VVbmRlclRlc3ROYW1lCiAgICBtYWtlR2xvYmFs
Q29uc3RhbnQgUGFja2FnZVVuZGVyVGVzdFN1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgKGpvaW4t
cGF0aCAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAkUGFja2FnZVVuZGVyVGVzdE5hbWUpCgog
ICAgbWFrZUdsb2JhbENvbnN0YW50IENvbG9yU2NoZW1lVW5pdFJlcG9zaXRvcnlVcmwgImh0dHBzOi8v
Z2l0aHViLmNvbS9nZXJhcmRyb2NoZS9zdWJsaW1lLWNvbG9yLXNjaGVtZS11bml0IgogICAgbWFrZUds
b2JhbENvbnN0YW50IENvbG9yU2NoZW1lVW5pdFN1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgKGpv
aW4tcGF0aCAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAnQ29sb3JTY2hlbWVVbml0JykKICAg
IG1ha2VHbG9iYWxDb25zdGFudCBDb3ZlcmFnZVJlcG9zaXRvcnlVcmwgImh0dHBzOi8vZ2l0aHViLmNv
bS9jb2RleG5zL3N1YmxpbWUtY292ZXJhZ2UiCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgQ292ZXJhZ2VT
dWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5IChqb2luLXBhdGggJFN1YmxpbWVUZXh0UGFja2FnZXNE
aXJlY3RvcnkgJ2NvdmVyYWdlJykKICAgIG1ha2VHbG9iYWxDb25zdGFudCBLZXlQcmVzc1JlcG9zaXRv
cnlVcmwgImh0dHBzOi8vZ2l0aHViLmNvbS9yYW5keTNrL0tleXByZXNzIgogICAgbWFrZUdsb2JhbENv
bnN0YW50IEtleVByZXNzU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAoam9pbi1wYXRoICRTdWJs
aW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5ICdLZXlwcmVzcycpCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQg
VW5pdFRlc3RpbmdSZXBvc2l0b3J5VXJsICJodHRwczovL2dpdGh1Yi5jb20vcmFuZHkzay9Vbml0VGVz
dGluZyIKICAgIG1ha2VHbG9iYWxDb25zdGFudCBVbml0VGVzdGluZ1N1YmxpbWVUZXh0UGFja2FnZXNE
aXJlY3RvcnkgKGpvaW4tcGF0aCAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAnVW5pdFRlc3Rp
bmcnKQoKICAgICMgVE9ETzogSXMgdGhpcyBzcGVjaWZpYyB0byB0aGUgQ0kgc2VydmljZT8KICAgICMg
U3VwcmVzcyBzb21lIGdpdCB3YXJuaW5ncwogICAgZ2l0IGNvbmZpZyAtLWdsb2JhbCBhZHZpY2UuZGV0
YWNoZWRIZWFkIGZhbHNlCn0='
)

    filter local:convertFromBase64String {
        param([string]$Content)
        $theContent = if ($_) { $_ } else { $Content }
        $utf8.GetString([System.Convert]::FromBase64String($theContent))
    }

    function local:createTextFile {
        param([string]$Destination, [string]$Content)
        if (![System.IO.Path]::IsPathRooted($Destination)) {
            throw "absolute path expected, got: $Destination"
        }
        if (test-path $Destination) {
            throw "cannot write file $Destination if it already exists"
        }
        [System.IO.File]::WriteAllText($Destination, $Content, $utf8)
    }

    filter local:unpackFile {
        param($Content)
        $theContent = if ($_) { $_ } else { $Content }
        # de-prettify and split
        $elements = @(($theContent -replace '\n','') -split '@@@')
        for ($i = 0; $i -lt $elements.length; $i = $i + 2) {
            createTextFile (join-path (convert-path .) $elements[$i]) ($elements[$i+1] | convertFromBase64String) -force
        }
    }

    push-location $UnitTestingPowerShellScriptsDirectory
        $encodedDependencies | unpackFile
    pop-location

    try {
        . $UnitTestingPowerShellScriptsDirectory\ci_config.ps1
    } catch [Exception]{
        # We dont't have access to  utils.ps1 yet. Use plain PS.
        write-error "$($error[0])"
        exit 1
    }

    $env:UNITTESTING_BOOTSTRAPPED = 1
}

. $UnitTestingPowerShellScriptsDirectory\ci_config.ps1
. $UnitTestingPowerShellScriptsDirectory\utils.ps1

function Bootstrap {
    [CmdletBinding()]
    param([switch] $with_color_scheme_unit)
    
    ensureCreateDirectory $SublimeTextPackagesDirectory

    # Copy plugin files to Packages/<Package> folder.
    if ($PackageUnderTestName -eq $SymbolCopyAll){
        logVerbose "creating directory for package under test at $PackageUnderTestSublimeTextPackagesDirectory..."
        ensureCreateDirectory $PackageUnderTestSublimeTextPackagesDirectory
        logVerbose "copying current directory contents to $PackageUnderTestSublimeTextPackagesDirectory..."
        # TODO: create junctions for all packages.
        ensureCopyDirectoryContents . $SublimeTextPackagesDirectory
    } else {
        logVerbose "creating directory junction to package under test at $PackageUnderTestSublimeTextPackagesDirectory..."
        ensureCreateDirectoryJunction $PackageUnderTestSublimeTextPackagesDirectory .
    }

    # Clone UnitTesting into Packages/UnitTesting.
    if (pathExists -Negate $UnitTestingSublimeTextPackagesDirectory) {
        $UNITTESTING_TAG = getLatestUnitTestingBuildTag $env:UNITTESTING_TAG $SublimeTextVersion $UnitTestingRepositoryUrl
        logVerbose "download UnitTesting tag: $UNITTESTING_TAG"
        gitCloneTag $UNITTESTING_TAG UnitTestingRepositoryUrl $UnitTestingSublimeTextPackagesDirectory
        gitGetHeadRevisionName $UnitTestingSublimeTextPackagesDirectory | logVerbose
        logVerbose ""
    }

    # Clone coverage plugin into Packages/coverage.
    installPackageForSublimeTextVersion3IfNotPresent $CoverageSublimeTextPackagesDirectory $env:COVERAGE_TAG $CoverageRepositoryUrl

    try {
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\install_sublime_text.ps1" -verbose
    } catch [Exception] {
        logError "$error[0]"
        exit 1
    }
}

function InstallPackageControl {
    remove-item $CoverageSublimeTextPackagesDirectory -Force -Recurse
    & "$UnitTestingSublimeTextPackagesDirectory\sbin\install_package_control.ps1" -verbose
}

function InstallColorSchemeUnit {
    installPackageForSublimeTextVersion3IfNotPresent $ColorSchemeUnitSublimeTextPackagesDirectory $env:COLOR_SCHEME_UNIT_TAG $ColorSchemeUnitRepositoryUrl
}

function InstallKeypress {
    installPackageForSublimeTextVersion3IfNotPresent $KeyPressSublimeTextPackagesDirectory $env:KEYPRESS_TAG $KeyPressRepositoryUrl
}

function RunTests {
    [CmdletBinding()]
    param(
        [switch] $syntax_test,
        [switch] $color_scheme_test,
        [switch] $coverage
    )

    if ($syntax_test) {
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -syntax_test
    } elseif ($color_scheme_test) {
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -color_scheme_test
    } elseif ($coverage) {
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" "$env:PACKAGE" -verbose -coverage
    } else {
        & "$UnitTestingSublimeTextPackagesDirectory\sbin\run_tests.ps1" "$env:PACKAGE" -verbose
    }

    stop-process -force -processname sublime_text -ea silentlycontinue
    start-sleep -seconds 2
}

try{
    switch ($command){
        'bootstrap' { Bootstrap }
        'install_package_control' { InstallPackageControl }
        'install_color_scheme_unit' { InstallColorSchemeUnit }
        'install_keypresss' { InstallKeypress }
        'run_tests' { RunTests -coverage:$coverage }
        'run_syntax_tests' { RunTests -syntax_test}
        'run_color_scheme_tests' { RunTests -color_scheme_test}
    }
}catch {
    throw $_
}