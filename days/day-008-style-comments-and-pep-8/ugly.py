import os
import sys
import math, json
from decimal import *

# TODO: fix this later
# print("old version")
# x = 1
# y = 2

l = "  Ada Lovelace,  ada@example.com , 36 , 1.75 , 70.5  "
O = 1
I = 0

data=l.strip( ).split(",")
NAME=data[ 0 ].strip().title()
Email = data[1].strip().lower()
age=int(data[2].strip())
h=float(data[3].strip())
W=float( data[4].strip() )

# calculate
bmi=W/(h**2)
x=bmi<18.5
y=bmi>=18.5 and bmi<25
z=bmi>=25 and bmi<30
w=bmi>=30

if_valid = age>0 and age<150 and h>0 and h<3 and W>0 and W<500

print ("="*60)
print("USER RECORD")
print("="*60)
print( "Name:  "+NAME )
print("Email: "+Email)
print("Age:   "+str(age))
print("Height:"+str(h)+"m")
print("Weight:"+str(W)+"kg")
print("BMI:   "+str(round(bmi,1))+"   (underweight="+str(x)+" healthy="+str(y)+" overweight="+str(z)+" obese="+str(w)+")")
print("Valid: "+str(if_valid))
print("="*60)

# check email
has_at = "@" in Email
has_dot = "." in Email
emailOK = has_at==True and has_dot==True
print("Email looks ok: "+str(emailOK))

# initials
parts=NAME.split()
inits=""
inits=inits+parts[0][0]
inits=inits+parts[1][0]
print("Initials: "+inits)

print("Age in months: "+str(age*12))
print("Age in days:   "+str(age*365))
print( "Height in cm:  "+str(h*100) )
print("Weight in lb:  "+str(round(W*2.20462,1)))
