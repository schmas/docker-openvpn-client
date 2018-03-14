#!/usr/bin/env python3
from glob      import glob
from os        import path
from os        import remove
from os        import symlink
from requests  import get
from shutil    import copyfileobj
from tempfile  import TemporaryDirectory
from zipfile   import ZipFile

# URL of the GoldenFrog config file archive
__url__ = "https://www.goldenfrog.com/openvpn/VyprVPNOpenVPNFiles.zip"

# Get the working directory for output
__this_dir__ = path.dirname(__file__)
if not __this_dir__:
    raise ValueError

# Delete old configs and certs
for extension in ("ovpn", "crt"):
    for file in glob(path.join(__this_dir__,"*.{}".format(extension))):
        remove(file)

# Download and extract the files
with TemporaryDirectory() as dir:
    out_file = path.join(dir, "VyperVPNOpenVPNFiles.zip")
    r = get(__url__, stream=True)
    if r.status_code == 200:
        with open(out_file, "wb") as f:
            r.raw.decode_content = True
            copyfileobj(r.raw, f)
        with ZipFile(out_file) as z:
            z.extractall(path=dir)
    # Import the 256 and 160 files
    for ver in ["160","256"]:
        files = glob(path.join(dir, "GFVyprVPNOpenVPNFiles/VyprVPNOpenVPNFiles/OpenVPN{}/*".format(ver)))
        for file in files:
            if path.basename(file) == "ca.vyprvpn.com.crt":
                out_file = path.join(__this_dir__, "ca.{}.crt".format(ver))
            else:
                out_file = path.basename(file.replace(".ovpn"," {}.ovpn".format(ver)))
                out_file = out_file.replace(" - ", " ")
                out_file = path.join(__this_dir__, out_file)

            # Rewrite the file as it is moved
            with open(file, "r") as f:
                out_lines = [l.strip() for l in f.readlines()]
            clean_out_lines = []
            for l in out_lines:
                if l == "auth-user-pass":
                    clean_out_lines.append("auth-user-pass /config/openvpn-credentials.txt")
                elif l == ";ca ca.vyprvpn.com.crt":
                    clean_out_lines.append(";ca /etc/openvpn/conf/vyprvpn/ca.crt")
                elif l == "<ca>":
                    clean_out_lines.append("script-security 2")
                    clean_out_lines.append("up /etc/openvpn/conf/vyprvpn/up.sh")
                    clean_out_lines.append("down /etc/openvpn/conf/vyprvpn/down.sh")
                    clean_out_lines.append("down-pre")
                    clean_out_lines.append(l)
                else:
                    clean_out_lines.append(l)
            with open(out_file, "w") as f:
                f.write("\n".join(clean_out_lines))

            # Create a 'default' symlink for the 256 version
            if ver == "256" and path.basename(file) != "ca.vyprvpn.com.crt":
                symlink(out_file, out_file.replace(" 256.ovpn", ".ovpn"))

# Create the defaults
symlink(path.join(__this_dir__, "ca.256.crt"), path.join(__this_dir__, "ca.crt"))
symlink(path.join(__this_dir__, "USA - New York 256.ovpn"), path.join(__this_dir__, "default.ovpn"))
