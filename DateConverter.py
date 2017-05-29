'''

Date conversions class

Author: 	Syd Pleno
Contact:	syd.pleno@gmail.com

'''

class DateConverter:
	
	# 00 25 77 ea 03 37 30 5f 02 00 = 29/11/2010 14:59:08
	
	@classmethod
	def GDtoJDN(self,GD): #DayOfMonth,Month,Year):
		# Gregorian Date to Julian Date Number
		# Source: http://quasar.as.utexas.edu/BillInfo/JulianDatesG.html
		(D,M,Y) = GD
		
		# If the month is January or February, subtract 1 from the year 
		# to get a new Y, and add 12 to the month to get a new M.
		if M < 3:
			Y -= 1
			M += 12
			
		A = Y/100
		B = A/4
		C = 2-A+B
		E = 365.25 * (Y+4716)
		F = 30.6001 * (M+1)
		JDN= int(C+D+E+F-1524.5)
		return JDN
		
	@classmethod
	def JDNtoGD(self,JD):
		# Julian Date Number to Gregorian Date
		# Source: http://quasar.as.utexas.edu/BillInfo/JulianDatesG.html
		Z = JD#+0.5
		W = int((Z - 1867216.25)/36524.25)
		X = int(W/4)
		A = Z+1+W-X
		B = A+1524
		C = int((B-122.1)/365.25)
		D = int(365.25 *C)
		E = int((B-D)/30.6001)
		F = int(30.6001 * E)
		DayOfMonth = int(B-D-F)
		if E > 12:
			Month=E-13
		else:
			Month = E-1 #or E-13 # (must get number less than or equal to 12)
		if Month < 3:
			Year = C-4715 
		else:
			Year = C-4716
		return (DayOfMonth, Month, Year)

if __name__ == "__main__":
	print DateConverter.JDNtoGD(2455978)
	print DateConverter.JDNtoGD(2455530)
	print DateConverter.JDNtoGD(2455227)
	print DateConverter.JDNtoGD(2455228)
	print DateConverter.GDtoJDN((31,1,2010))
	print DateConverter.JDNtoGD(2455229)
	print DateConverter.GDtoJDN((1,2,2010))
	print DateConverter.GDtoJDN((20,2,2012))
