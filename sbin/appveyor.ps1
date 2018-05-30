# NOTE: These params need to mirror exactly those of ci.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$command,
    [Parameter(Mandatory = $false)]
    [switch] $coverage
)

if (!$env:UNITTESTING_BOOTSTRAPPED) {
    write-output "[UnitTesting] bootstrapping environment..."

    # UTF8 encoding without preamble.
    $local:utf8 = [System.Text.UTF8Encoding]::new($false)
    $local:basePath = convert-path .

    # Files encoded in base64 encoding. They need to be unpacked before they can be used.
    # !!! Every time they change, they need to be regenerated and copied here. !!!
    $local:encodedDependencies = @(
        'utils.ps1@@@CmZ1bmN0aW9uIGVuc3VyZUNyZWF0ZURpcmVjdG9yeSB7CiAgICBwYXJhbShbc3RyaW5nXSRQYXRoKQogICAgW3ZvaWRdKG5ldy1pdGVtIC1pdGVtdHlwZSBkICIkUGF0aCIgLWZvcmNlIC1lcnJvcmFjdGlvbiBzdG9wKQp9CgpmaWx0ZXIgbG9nVmVyYm9zZSB7CiAgICBwYXJhbShbc3RyaW5nXSRtZXNzYWdlKQogICAgJG1zZyA9ICRtZXNzYWdlCiAgICBpZiAoJF8pIHsgJG1zZyA9ICIkXyIgfQogICAgd3JpdGUtdmVyYm9zZSAiW1VuaXRUZXN0aW5nXSAkbXNnIgp9CgpmaWx0ZXIgbG9nV2FybmluZyB7CiAgICBwYXJhbShbc3RyaW5nXSRtZXNzYWdlKQogICAgJG1zZyA9ICRtZXNzYWdlCiAgICBpZiAoJF8pIHsgJG1zZyA9ICIkXyIgfQogICAgd3JpdGUtd2FybmluZyAiW1VuaXRUZXN0aW5nXSAkbXNnIgp9CgpmdW5jdGlvbiBlbnN1cmVDb3B5RGlyZWN0b3J5Q29udGVudHMgewogICAgcGFyYW0oW3N0cmluZ10kUGF0aCwgW3N0cmluZ10kRGVzdGluYXRpb24pCiAgICBjb3B5LWl0ZW0gIiRQYXRoXCoiIC1yZWN1cnNlIC1mb3JjZSAkRGVzdGluYXRpb24gLWVycm9yYWN0aW9uIHN0b3AKfQoKZnVuY3Rpb24gZW5zdXJlUmVtb3ZlRGlyZWN0b3J5IHsKICAgIHBhcmFtKFtzdHJpbmddJFBhdGgpCiAgICBpZiAoW1N5c3RlbS5JTy5QYXRoLkZpbGVdLkV4aXN0cygoY29udmVydC1wYXRoICRQYXRoKSkpIHsKICAgICAgICB0aHJvdyAiZXhwZWN0ZWQgYSBkaXJlY3RvcnksIGdvdCBhIGZpbGU6ICRQYXRoIgogICAgfQogICAgcmVtb3ZlLWl0ZW0gIiRQYXRoIiAtcmVjdXJzZSAtZm9yY2UgLWVycm9yYWN0aW9uIHN0b3AKfQoKZnVuY3Rpb24gZ2V0TGF0ZXN0VGFnRnJvbVJlbW90ZSB7CiAgICBwYXJhbShbc3RyaW5nXSRVcmxUb1JlcG9zaXRvcnkpCiAgICBnaXQgbHMtcmVtb3RlIC0tdGFncyAiJFVybFRvUmVwb3NpdG9yeSIgfCAleyRfIC1yZXBsYWNlICIuKi8oLiopJCIsICckMSd9IGAKICAgICAgICB8IHdoZXJlLW9iamVjdCB7JF8gLW5vdG1hdGNoICJcXiJ9IHwle1tTeXN0ZW0uVmVyc2lvbl0kX30gYAogICAgICAgIHwgc29ydCB8IHNlbGVjdC1vYmplY3QgLWxhc3QgMSB8ICV7ICIkXyIgfQp9CgpmdW5jdGlvbiBnZXRMYXRlc3RVbml0VGVzdGluZ0J1aWxkVGFnIHsKICAgIHBhcmFtKFtzdHJpbmddJFRhZywgW3N0cmluZ10kU3VibGltZVRleHRWZXJzaW9uLCBbc3RyaW5nXSRVcmxUb1VuaXRUZXN0aW5nKQogICAgJHJlc3VsdCA9ICRUYWcKICAgIGlmIChbc3RyaW5nXTo6SXNOdWxsT3JFbXB0eSgkVGFnKSl7CiAgICAgICAgaWYgKCRTdWJsaW1lVGV4dFZlcnNpb24gLWVxIDIpIHsKICAgICAgICAgICAgJHJlc3VsdCA9ICcwLjEwLjYnCiAgICAgICAgfSBlbHNlaWYgKCRTdWJsaW1lVGV4dFZlcnNpb24gLWVxIDMpIHsKICAgICAgICAgICAgJHJlc3VsdCA9IGdldExhdGVzdFRhZ0Zyb21SZW1vdGUgJFVybFRvVW5pdFRlc3RpbmcKICAgICAgICB9CiAgICB9CiAgICAkcmVzdWx0Cn0KCmZ1bmN0aW9uIGdldExhdGVzdENvdmVyYWdlVGFnIHsKICAgIHBhcmFtKFtzdHJpbmddJFRhZywgW3N0cmluZ10kVXJsVG9Db3ZlcmFnZSkKICAgIGlmIChbc3RyaW5nXTo6SXNOdWxsT3JFbXB0eSgkVGFnKSkgeyBnZXRMYXRlc3RUYWdGcm9tUmVtb3RlICRVcmxUb0NvdmVyYWdlIH0KICAgIGVsc2UgeyAkVGFnIH0KfQoKZnVuY3Rpb24gZW5zdXJlQ3JlYXRlRGlyZWN0b3J5SnVuY3Rpb24gewogICAgcGFyYW0oW3N0cmluZ10kTGluaywgW3N0cmluZ10kVGFyZ2V0KQogICAgY21kLmV4ZSAvYyBta2xpbmsgL0ogIiRMaW5rIiAiJFRhcmdldCIKICAgIGlmICgkTEFTVEVYSVRDT0RFIC1uZSAwKSB7IHRocm93ICJjb3VsZCBub3QgY3JlYXRlIGRpcmVjdG9yeSBqdW5jdGlvbiBhdCAkTGluayB0byAkVGFyZ2V0IiB9Cn0='
        'ci.ps1@@@W0NtZGxldEJpbmRpbmcoKV0KcGFyYW0oCiAgICBbUGFyYW1ldGVyKE1hbmRhdG9yeSA9ICRmYWxzZSwgUG9zaXRpb24gPSAwKV0KICAgIFtzdHJpbmddJGNvbW1hbmQsCiAgICBbUGFyYW1ldGVyKE1hbmRhdG9yeSA9ICRmYWxzZSldCiAgICBbc3dpdGNoXSAkY292ZXJhZ2UKKQoKLiAkUFNTY3JpcHRSb290XHV0aWxzLnBzMQokU1RQID0gIkM6XHN0XERhdGFcUGFja2FnZXMiCiRzY3JpcHQ6UGFja2FnZU5hbWUgPSAkZW52OlBBQ0tBR0UKCmZ1bmN0aW9uIEJvb3RzdHJhcCB7CiAgICBbQ21kbGV0QmluZGluZygpXQogICAgcGFyYW0oCiAgICAgICAgW3N3aXRjaF0gJHdpdGhfY29sb3Jfc2NoZW1lX3VuaXQKICAgICkKICAgIAogICAgZW5zdXJlQ3JlYXRlRGlyZWN0b3J5ICRTVFAKCiAgICBpZiAoJFBhY2thZ2VOYW1lIC1lcSAiX19hbGxfXyIpewogICAgICAgIGxvZ1ZlcmJvc2UgImNyZWF0ZSBwYWNrYWdlIGRpcmVjdG9yeSBhdCAkU1RQXCRlbnY6UEFDS0FHRSIKICAgICAgICBlbnN1cmVDcmVhdGVEaXJlY3RvcnkgIiRTVFBcJFBhY2thZ2VOYW1lIgogICAgICAgIGxvZ1ZlcmJvc2UgImNvcHkgYWxsIHN1YmZvbGRlcnMgdG8gc3VibGltZSBwYWNrYWdlIGRpcmVjdG9yeSIKICAgICAgICAjIFRPRE86IGNyZWF0ZSBqdW5jdGlvbnMgZm9yIGFsbCBwYWNrYWdlcy4KICAgICAgICBlbnN1cmVDb3B5RGlyZWN0b3J5Q29udGVudHMgLiAiJFNUUCIKICAgIH0gZWxzZSB7CiAgICAgICAgbG9nVmVyYm9zZSAiY3JlYXRlIGRpcmVjdG9yeSBqdW5jdGlvbiB0byBwYWNrYWdlIGF0ICRTVFBcJFBhY2thZ2VOYW1lIgogICAgICAgIGVuc3VyZUNyZWF0ZURpcmVjdG9yeUp1bmN0aW9uICIkU1RQXCRlbnY6UEFDS0FHRSIgLgogICAgfQoKICAgIGdpdCBjb25maWcgLS1nbG9iYWwgYWR2aWNlLmRldGFjaGVkSGVhZCBmYWxzZQoKICAgICRVVF9QQVRIID0gIiRTVFBcVW5pdFRlc3RpbmciCiAgICBpZiAoISh0ZXN0LXBhdGggLXBhdGggIiRVVF9QQVRIIikpewoKICAgICAgICAkVVRfVVJMID0gImh0dHBzOi8vZ2l0aHViLmNvbS9yYW5keTNrL1VuaXRUZXN0aW5nIgogICAgICAgICRVTklUVEVTVElOR19UQUcgPSBnZXRMYXRlc3RVbml0VGVzdGluZ0J1aWxkVGFnICRlbnY6VU5JVFRFU1RJTkdfVEFHICRlbnY6U1VCTElNRV9URVhUX1ZFUlNJT04gJFVUX1VSTAoKICAgICAgICBsb2dWZXJib3NlICJkb3dubG9hZCBVbml0VGVzdGluZyB0YWc6ICRVTklUVEVTVElOR19UQUciCiAgICAgICAgZ2l0IGNsb25lIC0tcXVpZXQgLS1kZXB0aCAxIC0tYnJhbmNoPSRVTklUVEVTVElOR19UQUcgJFVUX1VSTCAiJFVUX1BBVEgiIDI+JG51bGwKICAgICAgICBnaXQgLUMgIiRVVF9QQVRIIiByZXYtcGFyc2UgSEVBRCB8IGxvZ1ZlcmJvc2UKICAgICAgICBsb2dWZXJib3NlICIiCiAgICB9CgogICAgJENPVl9QQVRIID0gIiRTVFBcY292ZXJhZ2UiCiAgICBpZiAoKCRlbnY6U1VCTElNRV9URVhUX1ZFUlNJT04gLWVxIDMpIC1hbmQgKCEodGVzdC1wYXRoIC1wYXRoICIkQ09WX1BBVEgiKSkpewoKICAgICAgICAkQ09WX1VSTCA9ICJodHRwczovL2dpdGh1Yi5jb20vY29kZXhucy9zdWJsaW1lLWNvdmVyYWdlIgogICAgICAgICRDT1ZFUkFHRV9UQUcgPSBnZXRMYXRlc3RDb3ZlcmFnZVRhZyAkZW52OkNPVkVSQUdFX1RBRyAkQ09WX1VSTAogICAgICAgIAogICAgICAgIGxvZ1ZlcmJvc2UgImRvd25sb2FkIHN1YmxpbWUtY292ZXJhZ2UgdGFnOiAkQ09WRVJBR0VfVEFHIgogICAgICAgIGdpdCBjbG9uZSAtLXF1aWV0IC0tZGVwdGggMSAtLWJyYW5jaD0kQ09WRVJBR0VfVEFHICRDT1ZfVVJMICIkQ09WX1BBVEgiIDI+JG51bGwKICAgICAgICBnaXQgLUMgIiRDT1ZfUEFUSCIgcmV2LXBhcnNlIEhFQUQgfCB3cml0ZS12ZXJib3NlCiAgICAgICAgbG9nVmVyYm9zZSAiIgogICAgfQoKICAgICYgIiRTVFBcVW5pdFRlc3Rpbmdcc2JpblxpbnN0YWxsX3N1YmxpbWVfdGV4dC5wczEiIC12ZXJib3NlCgp9CgpmdW5jdGlvbiBJbnN0YWxsUGFja2FnZUNvbnRyb2wgewogICAgJENPVl9QQVRIID0gIiRTVFBcY292ZXJhZ2UiCiAgICByZW1vdmUtaXRlbSAkQ09WX1BBVEggLUZvcmNlIC1SZWN1cnNlCiAgICAmICIkU1RQXFVuaXRUZXN0aW5nXHNiaW5caW5zdGFsbF9wYWNrYWdlX2NvbnRyb2wucHMxIiAtdmVyYm9zZQp9CgpmdW5jdGlvbiBJbnN0YWxsQ29sb3JTY2hlbWVVbml0IHsKICAgICRDU1VfUEFUSCA9ICIkU1RQXENvbG9yU2NoZW1lVW5pdCIKICAgIGlmICgoJGVudjpTVUJMSU1FX1RFWFRfVkVSU0lPTiAtZXEgMykgLWFuZCAoISh0ZXN0LXBhdGggLXBhdGggIiRDU1VfUEFUSCIpKSl7CiAgICAgICAgJENTVV9VUkwgPSAiaHR0cHM6Ly9naXRodWIuY29tL2dlcmFyZHJvY2hlL3N1YmxpbWUtY29sb3Itc2NoZW1lLXVuaXQiCgogICAgICAgIGlmICggJGVudjpDT0xPUl9TQ0hFTUVfVU5JVF9UQUcgLWVxICRudWxsKXsKICAgICAgICAgICAgIyB0aGUgbGF0ZXN0IHRhZwogICAgICAgICAgICAkQ09MT1JfU0NIRU1FX1VOSVRfVEFHID0gZ2l0IGxzLXJlbW90ZSAtLXRhZ3MgJENTVV9VUkwgfCAleyRfIC1yZXBsYWNlICIuKi8oLiopJCIsICckMSd9IGAKICAgICAgICAgICAgICAgICAgICB8IHdoZXJlLW9iamVjdCB7JF8gLW5vdG1hdGNoICJcXiJ9IHwle1tTeXN0ZW0uVmVyc2lvbl0kX30gYAogICAgICAgICAgICAgICAgICAgIHwgc29ydCB8IHNlbGVjdC1vYmplY3QgLWxhc3QgMSB8ICV7ICIkXyIgfQogICAgICAgIH0gZWxzZSB7CiAgICAgICAgICAgICRDT0xPUl9TQ0hFTUVfVU5JVF9UQUcgPSAkZW52OkNPTE9SX1NDSEVNRV9VTklUX1RBRwogICAgICAgIH0KICAgICAgICB3cml0ZS12ZXJib3NlICJkb3dubG9hZCBDb2xvclNjaGVtZVVuaXQgdGFnOiAkQ09MT1JfU0NIRU1FX1VOSVRfVEFHIgogICAgICAgIGdpdCBjbG9uZSAtLXF1aWV0IC0tZGVwdGggMSAtLWJyYW5jaD0kQ09MT1JfU0NIRU1FX1VOSVRfVEFHICRDU1VfVVJMICIkQ1NVX1BBVEgiIDI+JG51bGwKICAgICAgICBnaXQgLUMgIiRDU1VfUEFUSCIgcmV2LXBhcnNlIEhFQUQgfCB3cml0ZS12ZXJib3NlCiAgICAgICAgd3JpdGUtdmVyYm9zZSAiIgogICAgfQp9CgpmdW5jdGlvbiBJbnN0YWxsS2V5cHJlc3MgewogICAgJEtQX1BBVEggPSAiJFNUUFxLZXlwcmVzcyIKICAgIGlmICgoJGVudjpTVUJMSU1FX1RFWFRfVkVSU0lPTiAtZXEgMykgLWFuZCAoISh0ZXN0LXBhdGggLXBhdGggIiRLUF9QQVRIIikpKXsKICAgICAgICAkS1BfVVJMID0gImh0dHBzOi8vZ2l0aHViLmNvbS9yYW5keTNrL0tleXByZXNzIgoKICAgICAgICBpZiAoICRlbnY6S0VZUFJFU1NfVEFHIC1lcSAkbnVsbCl7CiAgICAgICAgICAgICMgdGhlIGxhdGVzdCB0YWcKICAgICAgICAgICAgJEtFWVBSRVNTX1RBRyA9IGdpdCBscy1yZW1vdGUgLS10YWdzICRLUF9VUkwgfCAleyRfIC1yZXBsYWNlICIuKi8oLiopJCIsICckMSd9IGAKICAgICAgICAgICAgICAgICAgICB8IHdoZXJlLW9iamVjdCB7JF8gLW5vdG1hdGNoICJcXiJ9IHwle1tTeXN0ZW0uVmVyc2lvbl0kX30gYAogICAgICAgICAgICAgICAgICAgIHwgc29ydCB8IHNlbGVjdC1vYmplY3QgLWxhc3QgMSB8ICV7ICIkXyIgfQogICAgICAgIH0gZWxzZSB7CiAgICAgICAgICAgICRLRVlQUkVTU19UQUcgPSAkZW52OktFWVBSRVNTX1RBRwogICAgICAgIH0KICAgICAgICB3cml0ZS12ZXJib3NlICJkb3dubG9hZCBDb2xvclNjaGVtZVVuaXQgdGFnOiAkS0VZUFJFU1NfVEFHIgogICAgICAgIGdpdCBjbG9uZSAtLXF1aWV0IC0tZGVwdGggMSAtLWJyYW5jaD0kS0VZUFJFU1NfVEFHICRLUF9VUkwgIiRLUF9QQVRIIiAyPiRudWxsCiAgICAgICAgZ2l0IC1DICIkS1BfUEFUSCIgcmV2LXBhcnNlIEhFQUQgfCB3cml0ZS12ZXJib3NlCiAgICAgICAgd3JpdGUtdmVyYm9zZSAiIgogICAgfQp9CgpmdW5jdGlvbiBSdW5UZXN0cyB7CiAgICBbQ21kbGV0QmluZGluZygpXQogICAgcGFyYW0oCiAgICAgICAgW3N3aXRjaF0gJHN5bnRheF90ZXN0LAogICAgICAgIFtzd2l0Y2hdICRjb2xvcl9zY2hlbWVfdGVzdAogICAgKQoKICAgIGlmICggJHN5bnRheF90ZXN0LklzUHJlc2VudCApewogICAgICAgICYgIiRTVFBcVW5pdFRlc3Rpbmdcc2JpblxydW5fdGVzdHMucHMxIiAiJGVudjpQQUNLQUdFIiAtdmVyYm9zZSAtc3ludGF4X3Rlc3QKICAgIH0gZWxzZWlmICggJGNvbG9yX3NjaGVtZV90ZXN0LklzUHJlc2VudCApewogICAgICAgICYgIiRTVFBcVW5pdFRlc3Rpbmdcc2JpblxydW5fdGVzdHMucHMxIiAiJGVudjpQQUNLQUdFIiAtdmVyYm9zZSAtY29sb3Jfc2NoZW1lX3Rlc3QKICAgIH0gZWxzZWlmICggJGNvdmVyYWdlLklzUHJlc2VudCApIHsKICAgICAgICAmICIkU1RQXFVuaXRUZXN0aW5nXHNiaW5ccnVuX3Rlc3RzLnBzMSIgIiRlbnY6UEFDS0FHRSIgLXZlcmJvc2UgLWNvdmVyYWdlCiAgICB9IGVsc2UgewogICAgICAgICYgIiRTVFBcVW5pdFRlc3Rpbmdcc2JpblxydW5fdGVzdHMucHMxIiAiJGVudjpQQUNLQUdFIiAtdmVyYm9zZQogICAgfQoKICAgIHN0b3AtcHJvY2VzcyAtZm9yY2UgLXByb2Nlc3NuYW1lIHN1YmxpbWVfdGV4dCAtZWEgc2lsZW50bHljb250aW51ZQogICAgc3RhcnQtc2xlZXAgLXNlY29uZHMgMgp9Cgp0cnl7CiAgICBzd2l0Y2ggKCRjb21tYW5kKXsKICAgICAgICAiYm9vdHN0cmFwIiB7IEJvb3RzdHJhcCB9CiAgICAgICAgImluc3RhbGxfcGFja2FnZV9jb250cm9sIiB7IEluc3RhbGxQYWNrYWdlQ29udHJvbCB9CiAgICAgICAgImluc3RhbGxfY29sb3Jfc2NoZW1lX3VuaXQiIHsgSW5zdGFsbENvbG9yU2NoZW1lVW5pdCB9CiAgICAgICAgImluc3RhbGxfa2V5cHJlc3NzIiB7IEluc3RhbGxLZXlwcmVzcyB9CiAgICAgICAgInJ1bl90ZXN0cyIgeyBSdW5UZXN0cyB9CiAgICAgICAgInJ1bl9zeW50YXhfdGVzdHMiIHsgUnVuVGVzdHMgLXN5bnRheF90ZXN0fQogICAgICAgICJydW5fY29sb3Jfc2NoZW1lX3Rlc3RzIiB7IFJ1blRlc3RzIC1jb2xvcl9zY2hlbWVfdGVzdH0KICAgIH0KfWNhdGNoIHsKICAgIHRocm93ICRfCn0='
        )

    filter local:convertToBase64String {
        param([string]$Path)
        $thePath = if ($_) { $_ } else { $Path }
        $content = get-content $thePath
        $content = $content -join "`n"
        [System.Convert]::ToBase64String($utf8.GetBytes($content))
    }

    filter local:convertFromBase64String {
        param([string]$Content)
        $theContent = if ($_) { $_ } else { $Content }
        $utf8.GetString([System.Convert]::FromBase64String($theContent))
    }

    function local:createTextFile {
        param([string]$Destination, [string]$Content)
        if (![System.IO.Path]::IsPathRooted($Destination)) {
            throw "absolute path expected, got: $Path"
        }
        if (!(test-path $Destination)) {
            [System.IO.File]::WriteAllText($Destination, $Content, $utf8)
        } else {
            throw "cannot write file $Destination if it already exists"
        }
    }

    filter local:unPackFile {
        param($Content)
        $theContent = if ($_) { $_ } else { $Content }
        $elements = @($theContent -split '@@@')
        for ($i = 0; $i -lt $elements.length; $i = $i + 2) {
            createTextFile (join-path $basePath $elements[$i]) ($elements[$i+1] | convertFromBase64String)
        }
    }

    $encodedDependencies | unPackFile

    . $PSScriptRoot\ci_config.ps1

    $env:UNITTESTING_BOOTSTRAPPED = 1
}

# Dependencies are now available to this script.
. $PSScriptRoot\utils.ps1

# logWarning "the appveyor.ps1 script is deprecated; use ci.ps1 instead"

# & $PSScriptRoot\ci.ps1 @PSBoundParameters

function Bootstrap {
    [CmdletBinding()]
    param(
        [switch] $with_color_scheme_unit
    )

    new-item -itemtype directory "$global:SublimeTextPackagesDirectory\$global:PackageUnderTestName" -force >$null

    if ($global:PackageUnderTestName -eq "__all__"){
        write-verbose "copy all subfolders to sublime package directory"
        copy * -recurse -force "$global:SublimeTextPackagesDirectory"
    } else {
        write-verbose "copy the package to sublime text Packages directory"
        copy * -recurse -force "$global:SublimeTextPackagesDirectory\$global:PackageUnderTestName"
    }

    git config --global advice.detachedHead false

    if (!(test-path -path "$global:UnitTestingSublimeTextPackagesDirectory")){

        if ( ${env:UNITTESTING_TAG} -eq $null){
            if ($global:IsSublimeText2) {
                $UNITTESTING_TAG = "0.10.6"
            } elseif ($global:IsSublimeText3) {
                # the latest tag
                $UNITTESTING_TAG = git ls-remote --tags $global:UnitTestingRepositoryUrl | %{$_ -replace ".*/(.*)$", '$1'} `
                        | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                        | sort | select-object -last 1 | %{ "$_" }
            }
        } else {
            $UNITTESTING_TAG = ${env:UNITTESTING_TAG}
        }

        write-verbose "download UnitTesting tag: $UNITTESTING_TAG"
        git clone --quiet --depth 1 --branch=$UNITTESTING_TAG $global:UnitTestingRepositoryUrl "$global:UnitTestingSublimeTextPackagesDirectory" 2>$null
        git -C "$global:UnitTestingSublimeTextPackagesDirectory" rev-parse HEAD | write-verbose
        write-verbose ""
    }

    $COV_PATH = "$global:SublimeTextPackagesDirectory\coverage"
    if ($global:IsSublimeTex3) -and (!(test-path -path "$COV_PATH"))){

        $COV_URL = "https://github.com/codexns/sublime-coverage"

        if ( ${env:COVERAGE_TAG} -eq $null){
            # the latest tag
            $COVERAGE_TAG = git ls-remote --tags $COV_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                    | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                    | sort | select-object -last 1 | %{ "$_" }
        } else {
            $COVERAGE_TAG = ${env:COVERAGE_TAG}
        }

        write-verbose "download sublime-coverage tag: $COVERAGE_TAG"
        git clone --quiet --depth 1 --branch=$COVERAGE_TAG $COV_URL "$COV_PATH" 2>$null
        git -C "$COV_PATH" rev-parse HEAD | write-verbose
        write-verbose ""
    }


    & "$global:SublimeTextPackagesDirectory\UnitTesting\sbin\install_sublime_text.ps1" -verbose

}

function InstallPackageControl {
    $COV_PATH = "$global:SublimeTextPackagesDirectory\coverage"
    remove-item $COV_PATH -Force -Recurse
    & "$global:SublimeTextPackagesDirectory\UnitTesting\sbin\install_package_control.ps1" -verbose
}

function InstallColorSchemeUnit {
    $CSU_PATH = "$global:SublimeTextPackagesDirectory\ColorSchemeUnit"
    if ($global:IsSublimeTex3) -and (!(test-path -path "$CSU_PATH"))){
        $CSU_URL = "https://github.com/gerardroche/sublime-color-scheme-unit"

        if ( ${env:COLOR_SCHEME_UNIT_TAG} -eq $null){
            # the latest tag
            $COLOR_SCHEME_UNIT_TAG = git ls-remote --tags $CSU_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                    | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                    | sort | select-object -last 1 | %{ "$_" }
        } else {
            $COLOR_SCHEME_UNIT_TAG = ${env:COLOR_SCHEME_UNIT_TAG}
        }
        write-verbose "download ColorSchemeUnit tag: $COLOR_SCHEME_UNIT_TAG"
        git clone --quiet --depth 1 --branch=$COLOR_SCHEME_UNIT_TAG $CSU_URL "$CSU_PATH" 2>$null
        git -C "$CSU_PATH" rev-parse HEAD | write-verbose
        write-verbose ""
    }
}

function InstallKeypress {
    $KP_PATH = "$global:SublimeTextPackagesDirectory\Keypress"
    if ($global:IsSublimeTex3) -and (!(test-path -path "$KP_PATH"))){
        $KP_URL = "https://github.com/randy3k/Keypress"

        if ( ${env:KEYPRESS_TAG} -eq $null){
            # the latest tag
            $KEYPRESS_TAG = git ls-remote --tags $KP_URL | %{$_ -replace ".*/(.*)$", '$1'} `
                    | where-object {$_ -notmatch "\^"} |%{[System.Version]$_} `
                    | sort | select-object -last 1 | %{ "$_" }
        } else {
            $KEYPRESS_TAG = ${env:KEYPRESS_TAG}
        }
        write-verbose "download ColorSchemeUnit tag: $KEYPRESS_TAG"
        git clone --quiet --depth 1 --branch=$KEYPRESS_TAG $KP_URL "$KP_PATH" 2>$null
        git -C "$KP_PATH" rev-parse HEAD | write-verbose
        write-verbose ""
    }
}

function RunTests {
    [CmdletBinding()]
    param(
        [switch] $syntax_test,
        [switch] $color_scheme_test
    )

    if ( $syntax_test.IsPresent ){
        & "$global:SublimeTextPackagesDirectory\UnitTesting\sbin\run_tests.ps1" "$global:PackageUnderTestName" -verbose -syntax_test
    } elseif ( $color_scheme_test.IsPresent ){
        & "$global:SublimeTextPackagesDirectory\UnitTesting\sbin\run_tests.ps1" "$global:PackageUnderTestName" -verbose -color_scheme_test
    } elseif ( $coverage.IsPresent ) {
        & "$global:SublimeTextPackagesDirectory\UnitTesting\sbin\run_tests.ps1" "$global:PackageUnderTestName" -verbose -coverage
    } else {
        & "$global:SublimeTextPackagesDirectory\UnitTesting\sbin\run_tests.ps1" "$global:PackageUnderTestName" -verbose
    }

    stop-process -force -processname sublime_text -ea silentlycontinue
    start-sleep -seconds 2
}

try{
    switch ($command){
        "bootstrap" { Bootstrap }
        "install_package_control" { InstallPackageControl }
        "install_color_scheme_unit" { InstallColorSchemeUnit }
        "install_keypresss" { InstallKeypress }
        "run_tests" { RunTests }
        "run_syntax_tests" { RunTests -syntax_test}
        "run_color_scheme_tests" { RunTests -color_scheme_test}
    }
}catch {
    throw $_
}