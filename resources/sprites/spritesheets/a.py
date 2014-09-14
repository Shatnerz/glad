def cycleList(list,step=1):
	"""Shifts each elements right if step is positive, left if negative"""
	newList = []
	r = range(len(list))
	r.reverse()
	if step < 0:
		step = abs(step) + len(list)-2
	for x in r:
		i=x-step
		while i<0:
			i += len(list)
		newList.append(list[i])
	newList.reverse()
	return newList
	
a=range(6)
print a

print cycleList(a,1)
print cycleList(a,-1)
