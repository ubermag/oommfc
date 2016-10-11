import subprocess


class OOMMF:
    def installed(self, package="oommf"):
        try:
            subprocess.check_call(["which", package])
        except subprocess.CalledProcessError:
            return False
        else:
            return True
