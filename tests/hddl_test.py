import subprocess

command = ('echo "this echo command' +
' has subquotes, spaces,\n\n" && echo "and newlines!"')

p = subprocess.Popen(command, universal_newlines=True,
                     shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
text = p.stdout.read()
retcode = p.wait()
print(text)