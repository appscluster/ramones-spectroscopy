#!/usr/bin/env python

import sys
import string
import matplotlib.pyplot as plt
from optparse import OptionParser, OptionGroup

#-------------------------------------------------------------------------------

parser = OptionParser(usage='./ramones.py --calc=calc.log')

group = OptionGroup(parser, 'Basic options')
group.add_option('--calc',
                 action='store',
                 default=None,
                 help='Calculated spectrum (frequencies and intensities)')
group.add_option('--min',
                 type='float',
                 action='store',
                 default=1000.0,
                 help='Min cm-1 [default: %default]')
group.add_option('--max',
                 type='float',
                 action='store',
                 default=1800.0,
                 help='Max cm-1 [default: %default]')
group.add_option('--hwhm',
                 type='float',
                 action='store',
                 default=8.0,
                 help='Lorentzian half-width at half-maximum [default: %default]')
group.add_option('--adjust',
                 action='store',
                 default=None,
                 help='''Adjust spectrum;
                         only move (1 anchor point) --adjust="1200=1250"
                         or scale (based on 2 achor points) --adjust="1200=1150 1550=1500"''')
parser.add_option_group(group)

(options, args) = parser.parse_args()

if len(sys.argv) == 1:
    # user has given no arguments and we are not in a test subdir: print help and exit
    print(parser.format_help().strip())
    sys.exit()

#-------------------------------------------------------------------------------

def normalize(l):
    largest = 0.0
    for i in range(len(l)):
        if abs(l[i]) > largest:
            largest = abs(l[i])
    for i in range(len(l)):
        l[i] = l[i]/largest
    return l

#-------------------------------------------------------------------------------

def get_lorentzians(x_l, f_l, i_l):

    y_l = []
    for i in range(len(x_l)):
        y_l.append(0.0)
    for i in range(len(x_l)):
        for j in range(len(f_l)):
            y_l[i] = y_l[i] + i_l[j]/(1 + (((x_l[i] - f_l[j])/options.hwhm)**2.0))

    return normalize(y_l)

#-------------------------------------------------------------------------------

if not options.calc:
    sys.exit('you have to specify --calc')

# here we will figure out the adjustment parameters g and s
# --adjust="f_1=ref_1 f_2=ref_2"
# so that we shift f_1 to ref_1 and f_2 to ref_2
# according to
# f_i' = g*f_i + s
# g    = (ref_1 - ref_2)/(f_1 - f_2)
# s    = 0.5*(ref_1 + ref_2) + 0.5*g*(f_1 + f_2)
s = 0.0
g = 1.0
if options.adjust:
   part1 = options.adjust.split()[0]
   f_1   = float(part1.split('=')[0])
   ref_1 = float(part1.split('=')[1])
   if len(options.adjust.split()) == 1:
      # 1 anchor point; only move
      s = ref_1 - f_1
   else:
      # 2 anchor points
      part2 = options.adjust.split()[1]
      f_2   = float(part2.split('=')[0])
      ref_2 = float(part2.split('=')[1])
      g    = (ref_1 - ref_2)/(f_1 - f_2)
      s    = 0.5*(ref_1 + ref_2) - 0.5*g*(f_1 + f_2)

# read freqs and intensities from calc output
f_l = []
i_l = []
for line in open(options.calc).readlines():
    if 'Frequencies ---' in line:
        for i in range(2, len(line.split())):
            f_l.append(s + g*float(line.split()[i]))
    if 'Raman Activities ---' in line:
        for i in range(3, len(line.split())):
            i_l.append(float(line.split()[i]))

# create list of x values
x_l = []
x = options.min
for i in range(int(options.max - options.min) + 1):
   x_l.append(x)
   x += 1.0

y_l = get_lorentzians(x_l, f_l, i_l)

# write sticks to file
f = file('xy.stick', 'w')
for i in range(len(f_l)):
    f.write("%f %f\n" % (f_l[i], i_l[i]))
f.close()

# write lorentzians to file
f = file('xy.lorentz', 'w')
for i in range(len(x_l)):
    f.write("%f %f\n" % (x_l[i], y_l[i]))
f.close()

# plot lorentzian plot on screen
plt.plot(x_l, y_l, linewidth=1.0)
plt.xlabel('frequency')
plt.ylabel('intensity')
plt.grid(True)
plt.show()
