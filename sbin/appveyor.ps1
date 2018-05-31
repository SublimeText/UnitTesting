# NOTE: These params need to mirror exactly those of ci.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)


# Scripts other than the bootstrapper are located here.
$global:UnitTestingPowerShellScriptsDirectory = $env:TEMP

if (!$env:UNITTESTING_BOOTSTRAPPED) {
    write-output "[UnitTesting] bootstrapping environment..."

    # UTF8 encoding without preamble.
    $local:utf8 = [System.Text.UTF8Encoding]::new($false)

    # Files encoded in base64 encoding. They need to be unpacked before they can be used.
    # !!! Every time they change, they need to be regenerated and copied here. !!!
    $local:encodedDependencies = @(
        'utils.ps1@@@CmZ1bmN0aW9uIGVuc3VyZUNyZWF0ZURpcmVjdG9yeSB7CiAgICBwYXJhbShbc3RyaW5nXSRQYXRoKQogICAgW3ZvaWRdKG5ldy1pdGVtIC1pdGVtdHlwZSBkICIkUGF0aCIgLWZvcmNlIC1lcnJvcmFjdGlvbiBzdG9wKQp9CgpmdW5jdGlvbiBlaXRoZXJPciB7CiAgICBwYXJhbSgkTGVmdCwgJFJpZ2h0KQogICAgaWYgKCRMZWZ0KSB7ICRMZWZ0IH0gZWxzZSB7ICRSaWdodCB9Cn0KCmZ1bmN0aW9uIG51bGxPciB7CiAgICBwYXJhbSgkTGVmdCwgJFJpZ2h0KQogICAgaWYgKCRMZWZ0IC1lcSAkbnVsbCkgeyAkTGVmdCB9IGVsc2UgeyAkUmlnaHQgfQp9CgpmdW5jdGlvbiB0b0xvZ01lc3NhZ2UgewogICAgcGFyYW0oW3N0cmluZ10kY29udGVudCkKICAgICJbVW5pdFRlc3RpbmddICRjb250ZW50Igp9CgpmaWx0ZXIgbG9nVmVyYm9zZSB7CiAgICBwYXJhbShbc3RyaW5nXSRtZXNzYWdlKQogICAgd3JpdGUtdmVyYm9zZSAodG9Mb2dNZXNzYWdlIChlaXRoZXJPciAkXyAkbWVzc2FnZSkpCn0KCmZpbHRlciBsb2dXYXJuaW5nIHsKICAgIHBhcmFtKFtzdHJpbmddJG1lc3NhZ2UpCiAgICB3cml0ZS13YXJuaW5nICh0b0xvZ01lc3NhZ2UgKGVpdGhlck9yICRfICRtZXNzYWdlKSkKfQoKZmlsdGVyIGxvZ0Vycm9yIHsKICAgIHBhcmFtKFtzdHJpbmddJG1lc3NhZ2UpCiAgICB3cml0ZS1lcnJvciAodG9Mb2dNZXNzYWdlIChlaXRoZXJPciAkXyAkbWVzc2FnZSkpCn0KCmZ1bmN0aW9uIGVuc3VyZUNvcHlEaXJlY3RvcnlDb250ZW50cyB7CiAgICBwYXJhbShbc3RyaW5nXSRQYXRoLCBbc3RyaW5nXSREZXN0aW5hdGlvbikKICAgIGNvcHktaXRlbSAiJFBhdGhcKiIgLXJlY3Vyc2UgLWZvcmNlICREZXN0aW5hdGlvbiAtZXJyb3JhY3Rpb24gc3RvcAp9CgpmdW5jdGlvbiBlbnN1cmVSZW1vdmVEaXJlY3RvcnkgewogICAgcGFyYW0oW3N0cmluZ10kUGF0aCkKICAgIGlmIChbU3lzdGVtLklPLlBhdGguRmlsZV0uRXhpc3RzKChjb252ZXJ0LXBhdGggJFBhdGgpKSkgewogICAgICAgIHRocm93ICJleHBlY3RlZCBhIGRpcmVjdG9yeSwgZ290IGEgZmlsZTogJFBhdGgiCiAgICB9CiAgICByZW1vdmUtaXRlbSAiJFBhdGgiIC1yZWN1cnNlIC1mb3JjZSAtZXJyb3JhY3Rpb24gc3RvcAp9CgpmdW5jdGlvbiBnaXRGZXRjaExhdGVzdFRhZ0Zyb21SZXBvc2l0b3J5IHsKICAgIHBhcmFtKFtzdHJpbmddJFVybFRvUmVwb3NpdG9yeSkKICAgIGdpdCBscy1yZW1vdGUgLS10YWdzICIkVXJsVG9SZXBvc2l0b3J5IiB8ICV7JF8gLXJlcGxhY2UgIi4qLyguKikkIiwgJyQxJ30gYAogICAgICAgIHwgd2hlcmUtb2JqZWN0IHskXyAtbm90bWF0Y2ggIlxeIn0gfCV7W1N5c3RlbS5WZXJzaW9uXSRffSBgCiAgICAgICAgfCBzb3J0IHwgc2VsZWN0LW9iamVjdCAtbGFzdCAxIHwgJXsgIiRfIiB9Cn0KCmZ1bmN0aW9uIGdpdENsb25lVGFnIHsKICAgIHBhcmFtKFtzdHJpbmddJFRhZywgW3N0cmluZ10kUmVwb3NpdG9yeVVybCwgW3N0cmluZ10kRGVzdGluYXRpb24pCiAgICBnaXQgY2xvbmUgLS1xdWlldCAtLWRlcHRoIDEgLS1icmFuY2g9JFRhZyAkUmVwb3NpdG9yeVVybCAiJERlc3RpbmF0aW9uIiAyPiRudWxsCn0KCmZ1bmN0aW9uIGdpdEdldEhlYWRSZXZpc2lvbk5hbWUgewogICAgcGFyYW0oW3N0cmluZ10kUmVwb3NpdG9yeURpcmVjdG9yeSkKICAgIGdpdCAtQyAkUmVwb3NpdG9yeURpcmVjdG9yeSByZXYtcGFyc2UgSEVBRAp9CgpmdW5jdGlvbiBnZXRMYXRlc3RVbml0VGVzdGluZ0J1aWxkVGFnIHsKICAgIHBhcmFtKFtzdHJpbmddJFRhZywgW3N0cmluZ10kU3VibGltZVRleHRWZXJzaW9uLCBbc3RyaW5nXSRVcmxUb1VuaXRUZXN0aW5nKQogICAgJHJlc3VsdCA9ICRUYWcKICAgIGlmIChbc3RyaW5nXTo6SXNOdWxsT3JFbXB0eSgkVGFnKSl7CiAgICAgICAgaWYgKCRTdWJsaW1lVGV4dFZlcnNpb24gLWVxIDIpIHsKICAgICAgICAgICAgJHJlc3VsdCA9ICcwLjEwLjYnCiAgICAgICAgfSBlbHNlaWYgKCRTdWJsaW1lVGV4dFZlcnNpb24gLWVxIDMpIHsKICAgICAgICAgICAgJHJlc3VsdCA9IGdpdEZldGNoTGF0ZXN0VGFnRnJvbVJlcG9zaXRvcnkgJFVybFRvVW5pdFRlc3RpbmcKICAgICAgICB9CiAgICB9CiAgICAkcmVzdWx0Cn0KCmZ1bmN0aW9uIGdldFJlcG9zaXRvcnlUYWcgewogICAgcGFyYW0oW3N0cmluZ10kUHJlZmVycmVkVGFnLCBbc3RyaW5nXSRSZXBvc2l0b3J5VXJsKQogICAgaWYgKFtzdHJpbmddOjpJc051bGxPckVtcHR5KCRQcmVmZXJyZWRUYWcpKSB7IGdpdEZldGNoTGF0ZXN0VGFnRnJvbVJlcG9zaXRvcnkgJFJlcG9zaXRvcnlVcmwgfQogICAgZWxzZSB7ICRQcmVmZXJyZWRUYWcgfQp9CgpmdW5jdGlvbiBjbG9uZVJlcG9zaXRvcnlUYWcgewogICAgcGFyYW0oW3N0cmluZ10kUHJlZmVycmVkVGFnLCBbc3RyaW5nXSRSZXBvc2l0b3J5VXJsLCBbc3RyaW5nXSREZXN0aW5hdGlvbikKICAgICRUYWcgPSBnZXRSZXBvc2l0b3J5VGFnICRQcmVmZXJyZWRUYWcgJFJlcG9zaXRvcnlVcmwKICAgIGxvZ1ZlcmJvc2UgImNsb25pbmcgJChzcGxpdC1wYXRoICRSZXBvc2l0b3J5VXJsIC1sZWFmKSB0YWc6ICRUYWcgaW50byAkRGVzdGluYXRpb24uLi4iCiAgICBnaXRDbG9uZVRhZyAkVGFnICRSZXBvc2l0b3J5VXJsICREZXN0aW5hdGlvbgogICAgZ2l0R2V0SGVhZFJldmlzaW9uTmFtZSAkRGVzdGluYXRpb24gfCBsb2dWZXJib3NlCiAgICBsb2dWZXJib3NlICIiCn0KCmZ1bmN0aW9uIGdldExhdGVzdENvbG9yU2NoZW1lVW5pdFRhZyB7CiAgICBwYXJhbShbc3RyaW5nXSRUYWcsIFtzdHJpbmddJFVybFRvQ29sb3JTY2hlbWVVbml0KQogICAgaWYgKFtzdHJpbmddOjpJc051bGxPckVtcHR5KCRUYWcpKSB7IGdpdEZldGNoTGF0ZXN0VGFnRnJvbVJlcG9zaXRvcnkgJFVybFRvQ29sb3JTY2hlbWVVbml0IH0KICAgIGVsc2UgeyAkVGFnIH0KfQoKZnVuY3Rpb24gZW5zdXJlQ3JlYXRlRGlyZWN0b3J5SnVuY3Rpb24gewogICAgcGFyYW0oW3N0cmluZ10kTGluaywgW3N0cmluZ10kVGFyZ2V0KQogICAgY21kLmV4ZSAvYyBta2xpbmsgL0ogIiRMaW5rIiAiJFRhcmdldCIKICAgIGlmICgkTEFTVEVYSVRDT0RFIC1uZSAwKSB7IHRocm93ICJjb3VsZCBub3QgY3JlYXRlIGRpcmVjdG9yeSBqdW5jdGlvbiBhdCAkTGluayB0byAkVGFyZ2V0IiB9Cn0KCmZ1bmN0aW9uIGVuc3VyZVZhbHVlIHsKICAgIHBhcmFtKCRWYWx1ZSwgW3N0cmluZ10kUGF0dGVybj0nXi4qJCcsIFtzdHJpbmddJE1lc3NhZ2U9JG51bGwpCiAgICBpZigoJFZhbHVlIC1lcSAkbnVsbCkgLW9yICgkVmFsdWUgLW5vdG1hdGNoICRQYXR0ZXJuKSkgewogICAgICAgIHRocm93IChlaXRoZXJPciAkTWVzc2FnZSAidmFsdWUgaXMgbnVsbCBvciB1bmV4cGVjdGVkIChleHBlY3RlZCBtYXRjaDogJFBhdHRlcm47IGdvdDogJFZhbHVlKSIpCiAgICB9CiAgICAkVmFsdWUKfQoKZnVuY3Rpb24gcGF0aEV4aXN0cyB7CiAgICBwYXJhbShbc3RyaW5nXSRQYXRoLCBbc3dpdGNoXSROZWdhdGU9JEZhbHNlKQogICAgaWYgKCEkTmVnYXRlKSB7IHRlc3QtcGF0aCAkUGF0aCB9IGVsc2UgeyAhKHRlc3QtcGF0aCAkUGF0aCkgfQp9CgpmdW5jdGlvbiBpbnN0YWxsUGFja2FnZUZvclN1YmxpbWVUZXh0VmVyc2lvbjNJZk5vdFByZXNlbnQgewogICAgcGFyYW0oW3N0cmluZ10kUGF0aCwgW3N0cmluZ10kUHJlZmVycmVkVGFnLCBbc3RyaW5nXSRSZXBvc2l0b3J5VXJsKQogICAgaWYgKCRJc1N1YmxpbWVUZXh0VmVyc2lvbjMgLWFuZCAocGF0aEV4aXN0cyAtTmVnYXRlICRQYXRoKSkgewogICAgICAgIGNsb25lUmVwb3NpdG9yeVRhZyAkUHJlZmVycmVkVGFnICRSZXBvc2l0b3J5VXJsICRQYXRoCiAgICB9Cn0=',
        'ci.ps1@@@W0NtZGxldEJpbmRpbmcoKV0KcGFyYW0oCiAgICBbUGFyYW1ldGVyKE1hbmRhdG9yeSA9ICRmYWxzZSwgUG9zaXRpb24gPSAwKV0KICAgIFtzdHJpbmddJGNvbW1hbmQsCiAgICBbUGFyYW1ldGVyKE1hbmRhdG9yeSA9ICRmYWxzZSldCiAgICBbc3dpdGNoXSAkY292ZXJhZ2UKKQoKIyBUT0RPOiBCb290c3RyYXAgdGhlIGJvb3RzdHJhcHBlci4gU2VlIGFwcHZleW9yLnBzMS4KJGdsb2JhbDpVbml0VGVzdGluZ1Bvd2VyU2hlbGxTY3JpcHRzRGlyZWN0b3J5ID0gJGVudjpURU1QCgouICRVbml0VGVzdGluZ1Bvd2VyU2hlbGxTY3JpcHRzRGlyZWN0b3J5XGNpX2NvbmZpZy5wczEKLiAkVW5pdFRlc3RpbmdQb3dlclNoZWxsU2NyaXB0c0RpcmVjdG9yeVx1dGlscy5wczEKCmZ1bmN0aW9uIEJvb3RzdHJhcCB7CiAgICBbQ21kbGV0QmluZGluZygpXQogICAgcGFyYW0oW3N3aXRjaF0gJHdpdGhfY29sb3Jfc2NoZW1lX3VuaXQpCiAgICAKICAgIGVuc3VyZUNyZWF0ZURpcmVjdG9yeSAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeQoKICAgICMgQ29weSBwbHVnaW4gZmlsZXMgdG8gUGFja2FnZXMvPFBhY2thZ2U+IGZvbGRlci4KICAgIGlmICgkUGFja2FnZVVuZGVyVGVzdE5hbWUgLWVxICRTeW1ib2xDb3B5QWxsKXsKICAgICAgICBsb2dWZXJib3NlICJjcmVhdGluZyBkaXJlY3RvcnkgZm9yIHBhY2thZ2UgdW5kZXIgdGVzdCBhdCAkUGFja2FnZVVuZGVyVGVzdFN1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkuLi4iCiAgICAgICAgZW5zdXJlQ3JlYXRlRGlyZWN0b3J5ICRQYWNrYWdlVW5kZXJUZXN0U3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeQogICAgICAgIGxvZ1ZlcmJvc2UgImNvcHlpbmcgY3VycmVudCBkaXJlY3RvcnkgY29udGVudHMgdG8gJFBhY2thZ2VVbmRlclRlc3RTdWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5Li4uIgogICAgICAgICMgVE9ETzogY3JlYXRlIGp1bmN0aW9ucyBmb3IgYWxsIHBhY2thZ2VzLgogICAgICAgIGVuc3VyZUNvcHlEaXJlY3RvcnlDb250ZW50cyAuICRTdWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5CiAgICB9IGVsc2UgewogICAgICAgIGxvZ1ZlcmJvc2UgImNyZWF0aW5nIGRpcmVjdG9yeSBqdW5jdGlvbiB0byBwYWNrYWdlIHVuZGVyIHRlc3QgYXQgJFBhY2thZ2VVbmRlclRlc3RTdWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5Li4uIgogICAgICAgIGVuc3VyZUNyZWF0ZURpcmVjdG9yeUp1bmN0aW9uICRQYWNrYWdlVW5kZXJUZXN0U3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAuCiAgICB9CgogICAgIyBDbG9uZSBVbml0VGVzdGluZyBpbnRvIFBhY2thZ2VzL1VuaXRUZXN0aW5nLgogICAgaWYgKHBhdGhFeGlzdHMgLU5lZ2F0ZSAkVW5pdFRlc3RpbmdTdWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5KSB7CiAgICAgICAgJFVOSVRURVNUSU5HX1RBRyA9IGdldExhdGVzdFVuaXRUZXN0aW5nQnVpbGRUYWcgJGVudjpVTklUVEVTVElOR19UQUcgJFN1YmxpbWVUZXh0VmVyc2lvbiAkVW5pdFRlc3RpbmdSZXBvc2l0b3J5VXJsCiAgICAgICAgbG9nVmVyYm9zZSAiZG93bmxvYWQgVW5pdFRlc3RpbmcgdGFnOiAkVU5JVFRFU1RJTkdfVEFHIgogICAgICAgIGdpdENsb25lVGFnICRVTklUVEVTVElOR19UQUcgVW5pdFRlc3RpbmdSZXBvc2l0b3J5VXJsICRVbml0VGVzdGluZ1N1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkKICAgICAgICBnaXRHZXRIZWFkUmV2aXNpb25OYW1lICRVbml0VGVzdGluZ1N1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgfCBsb2dWZXJib3NlCiAgICAgICAgbG9nVmVyYm9zZSAiIgogICAgfQoKICAgICMgQ2xvbmUgY292ZXJhZ2UgcGx1Z2luIGludG8gUGFja2FnZXMvY292ZXJhZ2UuCiAgICBpbnN0YWxsUGFja2FnZUZvclN1YmxpbWVUZXh0VmVyc2lvbjNJZk5vdFByZXNlbnQgJENvdmVyYWdlU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAkZW52OkNPVkVSQUdFX1RBRyAkQ292ZXJhZ2VSZXBvc2l0b3J5VXJsCgogICAgJiAiJFVuaXRUZXN0aW5nU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeVxzYmluXGluc3RhbGxfc3VibGltZV90ZXh0LnBzMSIgLXZlcmJvc2UKfQoKZnVuY3Rpb24gSW5zdGFsbFBhY2thZ2VDb250cm9sIHsKICAgIHJlbW92ZS1pdGVtICRDb3ZlcmFnZVN1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgLUZvcmNlIC1SZWN1cnNlCiAgICAmICIkVW5pdFRlc3RpbmdTdWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5XHNiaW5caW5zdGFsbF9wYWNrYWdlX2NvbnRyb2wucHMxIiAtdmVyYm9zZQp9CgpmdW5jdGlvbiBJbnN0YWxsQ29sb3JTY2hlbWVVbml0IHsKICAgIGluc3RhbGxQYWNrYWdlRm9yU3VibGltZVRleHRWZXJzaW9uM0lmTm90UHJlc2VudCAkQ29sb3JTY2hlbWVVbml0U3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAkZW52OkNPTE9SX1NDSEVNRV9VTklUX1RBRyAkQ29sb3JTY2hlbWVVbml0UmVwb3NpdG9yeVVybAp9CgpmdW5jdGlvbiBJbnN0YWxsS2V5cHJlc3MgewogICAgaW5zdGFsbFBhY2thZ2VGb3JTdWJsaW1lVGV4dFZlcnNpb24zSWZOb3RQcmVzZW50ICRLZXlQcmVzc1N1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgJGVudjpLRVlQUkVTU19UQUcgJEtleVByZXNzUmVwb3NpdG9yeVVybAp9CgpmdW5jdGlvbiBSdW5UZXN0cyB7CiAgICBbQ21kbGV0QmluZGluZygpXQogICAgcGFyYW0oCiAgICAgICAgW3N3aXRjaF0gJHN5bnRheF90ZXN0LAogICAgICAgIFtzd2l0Y2hdICRjb2xvcl9zY2hlbWVfdGVzdCwKICAgICAgICBbc3dpdGNoXSAkY292ZXJhZ2UKICAgICkKCiAgICBpZiAoJHN5bnRheF90ZXN0KSB7CiAgICAgICAgJiAiJFVuaXRUZXN0aW5nU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeVxzYmluXHJ1bl90ZXN0cy5wczEiICIkZW52OlBBQ0tBR0UiIC12ZXJib3NlIC1zeW50YXhfdGVzdAogICAgfSBlbHNlaWYgKCRjb2xvcl9zY2hlbWVfdGVzdCkgewogICAgICAgICYgIiRVbml0VGVzdGluZ1N1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3Rvcnlcc2JpblxydW5fdGVzdHMucHMxIiAiJGVudjpQQUNLQUdFIiAtdmVyYm9zZSAtY29sb3Jfc2NoZW1lX3Rlc3QKICAgIH0gZWxzZWlmICgkY292ZXJhZ2UpIHsKICAgICAgICAmICIkVW5pdFRlc3RpbmdTdWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5XHNiaW5ccnVuX3Rlc3RzLnBzMSIgIiRlbnY6UEFDS0FHRSIgLXZlcmJvc2UgLWNvdmVyYWdlCiAgICB9IGVsc2UgewogICAgICAgICYgIiRVbml0VGVzdGluZ1N1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3Rvcnlcc2JpblxydW5fdGVzdHMucHMxIiAiJGVudjpQQUNLQUdFIiAtdmVyYm9zZQogICAgfQoKICAgIHN0b3AtcHJvY2VzcyAtZm9yY2UgLXByb2Nlc3NuYW1lIHN1YmxpbWVfdGV4dCAtZWEgc2lsZW50bHljb250aW51ZQogICAgc3RhcnQtc2xlZXAgLXNlY29uZHMgMgp9Cgp0cnl7CiAgICBzd2l0Y2ggKCRjb21tYW5kKXsKICAgICAgICAnYm9vdHN0cmFwJyB7IEJvb3RzdHJhcCB9CiAgICAgICAgJ2luc3RhbGxfcGFja2FnZV9jb250cm9sJyB7IEluc3RhbGxQYWNrYWdlQ29udHJvbCB9CiAgICAgICAgJ2luc3RhbGxfY29sb3Jfc2NoZW1lX3VuaXQnIHsgSW5zdGFsbENvbG9yU2NoZW1lVW5pdCB9CiAgICAgICAgJ2luc3RhbGxfa2V5cHJlc3NzJyB7IEluc3RhbGxLZXlwcmVzcyB9CiAgICAgICAgJ3J1bl90ZXN0cycgeyBSdW5UZXN0cyAtY292ZXJhZ2U6JGNvdmVyYWdlIH0KICAgICAgICAncnVuX3N5bnRheF90ZXN0cycgeyBSdW5UZXN0cyAtc3ludGF4X3Rlc3R9CiAgICAgICAgJ3J1bl9jb2xvcl9zY2hlbWVfdGVzdHMnIHsgUnVuVGVzdHMgLWNvbG9yX3NjaGVtZV90ZXN0fQogICAgfQp9Y2F0Y2ggewogICAgdGhyb3cgJF8KfQ==',
        'ci_config.ps1@@@LiAkUFNTY3JpcHRSb290XHV0aWxzLnBzMQoKIyBXZSBtdXN0IHNldCBjb25zdGFudHMgb25seSBvbmNlLgppZiAoISRlbnY6VU5JVFRFU1RJTkdfQk9PVFNUUkFQUEVEKSB7CiAgICBmdW5jdGlvbiBsb2NhbDptYWtlR2xvYmFsQ29uc3RhbnQgewogICAgICAgIHBhcmFtKFtzdHJpbmddJE5hbWUsICRWYWx1ZSkKICAgICAgICBuZXctdmFyaWFibGUgLW5hbWUgJE5hbWUgLXZhbHVlICRWYWx1ZSAtb3B0aW9uIGNvbnN0YW50IC1zY29wZSBnbG9iYWwKICAgIH0KCiAgICBsb2dWZXJib3NlICJzZXR0aW5nIGdsb2JhbCBjb25zdGFudHMgYW5kIHZhcmlhYmxlcy4uLiIKCiAgICAkZW52OlBBQ0tBR0UgPSAiIgoKICAgICMgVE9ETzogSWYgd2UgdXNlZCBkaXJlY3RvcnkganVuY3Rpb25zIGhlcmUgdG9vLCB3ZSB3b3VsZG4ndCBuZWVkIHRoaXM/CiAgICAjIFRoaXMgY29uc3RhbnQgbWVhbnMgdGhhdCB0aGUgZW50aXJlIGNvbnRlbnRzIG9mIHRoZSBzb3VyY2UgZGlyZWN0b3J5IG11c3QgYmUgY29waWVkIHRvIHRoZSB0YXJnZXQgZGlyZWN0b3J5LgogICAgbWFrZUdsb2JhbENvbnN0YW50IFN5bWJvbENvcHlBbGwgJ19fYWxsX18nCgogICAgbWFrZUdsb2JhbENvbnN0YW50IFN1YmxpbWVUZXh0VmVyc2lvbiAoZW5zdXJlVmFsdWUgJGVudjpTVUJMSU1FX1RFWFRfVkVSU0lPTiAnXjJ8MyQnIC1tZXNzYWdlICJ0aGUgZW52aXJvbm1lbnQgdmFyaWFibGUgU1VCTElNRV9URVhUX1ZFUlNJT04gbXVzdCBiZSBzZXQgdG8gJzInIG9yICczJyIpCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgSXNTdWJsaW1lVGV4dFZlcnNpb24zICgkU3VibGltZVRleHRWZXJzaW9uIC1lcSAzKQogICAgbWFrZUdsb2JhbENvbnN0YW50IElzU3VibGltZVRleHRWZXJzaW9uMiAoJFN1YmxpbWVUZXh0VmVyc2lvbiAtZXEgMikKICAgIG1ha2VHbG9iYWxDb25zdGFudCBTdWJsaW1lVGV4dERpcmVjdG9yeSAoZWl0aGVyT3IgJGVudjpTVUJMSU1FX1RFWFRfRElSRUNUT1JZICJDOlxzdCIpCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgU3VibGltZVRleHRFeGVjdXRhYmxlSGVscGVyUGF0aCAoam9pbi1wYXRoICRTdWJsaW1lVGV4dERpcmVjdG9yeSAnc3VibC5leGUnKQogICAgbWFrZUdsb2JhbENvbnN0YW50IFN1YmxpbWVUZXh0RXhlY3V0YWJsZVBhdGggKGpvaW4tcGF0aCAkU3VibGltZVRleHREaXJlY3RvcnkgJ3N1YmxpbWVfdGV4dC5leGUnKQogICAgbWFrZUdsb2JhbENvbnN0YW50IFN1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgKGVpdGhlck9yICRlbnY6U1VCTElNRV9URVhUX1BBQ0tBR0VTX0RJUkVDVE9SWSAiQzpcc3RcRGF0YVxQYWNrYWdlcyIpCiAgICAjIFRPRE86IEZvciBjb21wYXRpYmlsaXR5OyByZW1vdmUgd2hlbiBub3QgdXNlZCBhbnltb3JlLgogICAgJGdsb2JhbDpTVFAgPSAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeQoKICAgIG1ha2VHbG9iYWxDb25zdGFudCBQYWNrYWdlVW5kZXJUZXN0TmFtZSAoZW5zdXJlVmFsdWUgKGVpdGhlck9yICRlbnY6VU5JVFRFU1RJTkdfUEFDS0FHRV9VTkRFUl9URVNUX05BTUUgJGVudjpQQUNLQUdFKSAtbWVzc2FnZSAidGhlIGVudmlyb25tZW50IHZhcmlhYmxlIFVOSVRURVNUSU5HX1BBQ0tBR0VfVU5ERVJfVEVTVF9OQU1FIChvciBhbHRlcm5hdGl2ZWx5LCBQQUNLQUdFKSBpcyBub3Qgc2V0IikKICAgICMgVE9ETzogRm9yIGNvbXBhdGliaWxpdHk7IHJlbW92ZSB3aGVuIG5vdCB1c2VkIGFueW1vcmUuCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgUGFja2FnZU5hbWUgJFBhY2thZ2VVbmRlclRlc3ROYW1lCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgUGFja2FnZVVuZGVyVGVzdFN1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgKGpvaW4tcGF0aCAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAkUGFja2FnZVVuZGVyVGVzdE5hbWUpCgogICAgbWFrZUdsb2JhbENvbnN0YW50IENvbG9yU2NoZW1lVW5pdFJlcG9zaXRvcnlVcmwgImh0dHBzOi8vZ2l0aHViLmNvbS9nZXJhcmRyb2NoZS9zdWJsaW1lLWNvbG9yLXNjaGVtZS11bml0IgogICAgbWFrZUdsb2JhbENvbnN0YW50IENvbG9yU2NoZW1lVW5pdFN1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgKGpvaW4tcGF0aCAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAnQ29sb3JTY2hlbWVVbml0JykKICAgIG1ha2VHbG9iYWxDb25zdGFudCBDb3ZlcmFnZVJlcG9zaXRvcnlVcmwgImh0dHBzOi8vZ2l0aHViLmNvbS9jb2RleG5zL3N1YmxpbWUtY292ZXJhZ2UiCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgQ292ZXJhZ2VTdWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5IChqb2luLXBhdGggJFN1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgJ2NvdmVyYWdlJykKICAgIG1ha2VHbG9iYWxDb25zdGFudCBLZXlQcmVzc1JlcG9zaXRvcnlVcmwgImh0dHBzOi8vZ2l0aHViLmNvbS9yYW5keTNrL0tleXByZXNzIgogICAgbWFrZUdsb2JhbENvbnN0YW50IEtleVByZXNzU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAoam9pbi1wYXRoICRTdWJsaW1lVGV4dFBhY2thZ2VzRGlyZWN0b3J5ICdLZXlwcmVzcycpCiAgICBtYWtlR2xvYmFsQ29uc3RhbnQgVW5pdFRlc3RpbmdSZXBvc2l0b3J5VXJsICJodHRwczovL2dpdGh1Yi5jb20vcmFuZHkzay9Vbml0VGVzdGluZyIKICAgIG1ha2VHbG9iYWxDb25zdGFudCBVbml0VGVzdGluZ1N1YmxpbWVUZXh0UGFja2FnZXNEaXJlY3RvcnkgKGpvaW4tcGF0aCAkU3VibGltZVRleHRQYWNrYWdlc0RpcmVjdG9yeSAnVW5pdFRlc3RpbmcnKQoKICAgICMgVE9ETzogSXMgdGhpcyBzcGVjaWZpYyB0byB0aGUgQ0kgc2VydmljZT8KICAgICMgU3VwcmVzcyBzb21lIGdpdCB3YXJuaW5ncwogICAgZ2l0IGNvbmZpZyAtLWdsb2JhbCBhZHZpY2UuZGV0YWNoZWRIZWFkIGZhbHNlCn0='
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
        $elements = @($theContent -split '@@@')
        for ($i = 0; $i -lt $elements.length; $i = $i + 2) {
            createTextFile (join-path (convert-path .) $elements[$i]) ($elements[$i+1] | convertFromBase64String)
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

# Dependencies are now available to this script.
. $UnitTestingPowerShellScriptsDirectory\utils.ps1

# logWarning "the appveyor.ps1 script is deprecated; use ci.ps1 instead"

& $UnitTestingPowerShellScriptsDirectory\ci.ps1 @PSBoundParameters
