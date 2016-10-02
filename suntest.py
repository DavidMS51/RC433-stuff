from subprocess import Popen, PIPE

p = Popen(['/usr/local/bin/sunwait','-p','51.72N','.6502W'], stdout=PIPE, stderr=PIPE, stdin=PIPE)

output = p.stdout.read()
print output

stpos =  output.find("rises")

print stpos

rise = output[stpos+6:stpos+8]+':'+output[stpos+8:stpos+11]
set  = output[stpos+21:stpos+23]+':'+output[stpos+23:stpos+25]


print 'rises = ',rise
print 'sets = ',set

