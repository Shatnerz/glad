import sys, pygame
pygame.init()

size = width, height = 768, 33
black = 0,0,0

screen = pygame.display.set_mode(size,0,8)

tile = pygame.image.load("firelem.png").convert(8)
alpha = tile.get_at((2,2))
tile.set_colorkey(alpha)
tileRect = tile.get_rect()

palette = tile.get_palette()
palette = [[0, 0, 0, 255], [32, 32, 32, 255], [64, 64, 64, 255], [96, 96, 96, 255], [128, 128, 128, 255], [160, 160, 160, 255], 
           [192, 192, 192, 255], [224, 224, 224, 255], [4, 4, 4, 255], [36, 36, 36, 255], [68, 68, 68, 255], [100, 100, 100, 255], 
           [132, 132, 132, 255], [164, 164, 164, 255], [196, 196, 196, 255], [228, 228, 228, 255], [0, 0, 0, 255], [60, 60, 60, 255], 
           [72, 72, 72, 255], [84, 84, 84, 255], [96, 96, 96, 255], [108, 108, 108, 255], [120, 120, 120, 255], [132, 132, 132, 255], 
           [144, 144, 144, 255], [156, 156, 156, 255], [168, 168, 168, 255], [180, 180, 180, 255], [192, 192, 192, 255], 
           [204, 204, 204, 255], [216, 216, 216, 255], [228, 228, 228, 255], [228, 64, 64, 255], [216, 72, 72, 255], 
           [204, 80, 80, 255], [192, 88, 88, 255], [180, 96, 96, 255], [168, 104, 104, 255], [156, 112, 112, 255], 
           [144, 120, 120, 255], [228, 0, 0, 255], [208, 0, 0, 255], [188, 0, 0, 255], [168, 0, 0, 255], [148, 0, 0, 255], 
           [128, 0, 0, 255], [108, 0, 0, 255], [88, 0, 0, 255], [64, 228, 64, 255], [72, 216, 72, 255], [80, 204, 80, 255], 
           [88, 192, 88, 255], [96, 180, 96, 255], [104, 168, 104, 255], [112, 156, 112, 255], [120, 144, 120, 255], [0, 228, 0, 255], 
           [0, 208, 0, 255], [0, 188, 0, 255], [0, 168, 0, 255], [0, 148, 0, 255], [0, 128, 0, 255], [0, 108, 0, 255], [0, 88, 0, 255], 
           [64, 64, 228, 255], [72, 72, 216, 255], [80, 80, 204, 255], [88, 88, 192, 255], [96, 96, 180, 255], [104, 104, 168, 255], 
           [112, 112, 156, 255], [120, 120, 144, 255], [0, 0, 228, 255], [0, 0, 208, 255], [0, 0, 188, 255], [0, 0, 168, 255], 
           [0, 0, 148, 255], [0, 0, 128, 255], [0, 0, 108, 255], [0, 0, 88, 255], [228, 228, 64, 255], [216, 216, 72, 255], 
           [204, 204, 80, 255], [192, 192, 88, 255], [180, 180, 96, 255], [168, 168, 104, 255], [156, 156, 112, 255], 
           [144, 144, 120, 255], [228, 228, 0, 255], [208, 208, 0, 255], [188, 188, 0, 255], [168, 168, 0, 255], [148, 148, 0, 255], 
           [128, 128, 0, 255], [108, 108, 0, 255], [88, 88, 0, 255], [228, 64, 228, 255], [216, 72, 216, 255], [204, 80, 204, 255], 
           [192, 88, 192, 255], [180, 96, 180, 255], [168, 104, 168, 255], [156, 112, 156, 255], [144, 120, 144, 255], 
           [228, 0, 228, 255], [208, 0, 208, 255], [188, 0, 188, 255], [168, 0, 168, 255], [148, 0, 148, 255], [128, 0, 128, 255], 
           [108, 0, 108, 255], [88, 0, 88, 255], [64, 228, 228, 255], [72, 216, 216, 255], [80, 204, 204, 255], [88, 192, 192, 255], 
           [96, 180, 180, 255], [104, 168, 168, 255], [112, 156, 156, 255], [120, 144, 144, 255], [0, 228, 228, 255], [0, 208, 208, 255], 
           [0, 188, 188, 255], [0, 168, 168, 255], [0, 148, 148, 255], [0, 128, 128, 255], [0, 108, 108, 255], [0, 88, 88, 255], 
           [228, 164, 100, 255], [208, 144, 80, 255], [188, 124, 60, 255], [168, 104, 40, 255], [148, 84, 20, 255], [128, 64, 0, 255], 
           [108, 44, 0, 255], [88, 24, 0, 255], [200, 160, 120, 255], [180, 140, 100, 255], [160, 120, 80, 255], [140, 100, 60, 255], 
           [120, 80, 40, 255], [100, 60, 20, 255], [80, 40, 0, 255], [60, 20, 0, 255], [228, 100, 164, 255], [208, 80, 144, 255], 
           [188, 60, 124, 255], [168, 40, 104, 255], [148, 20, 84, 255], [128, 0, 64, 255], [108, 0, 44, 255], [88, 0, 24, 255], 
           [200, 120, 160, 255], [180, 100, 140, 255], [160, 80, 120, 255], [140, 60, 100, 255], [120, 40, 80, 255], 
           [100, 20, 60, 255], [80, 0, 40, 255], [60, 0, 20, 255], [0, 72, 24, 255], [0, 64, 24, 255], [0, 52, 20, 255], 
           [0, 44, 20, 255], [0, 32, 12, 255], [0, 24, 8, 255], [0, 12, 4, 255], [0, 8, 0, 255], [68, 68, 68, 255], [68, 68, 68, 255], 
           [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], 
           [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], 
           [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], 
           [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [68, 68, 68, 255], [164, 100, 228, 255], [144, 80, 208, 255], 
           [124, 60, 188, 255], [104, 40, 168, 255], [84, 20, 148, 255], [64, 0, 128, 255], [44, 0, 108, 255], [24, 0, 88, 255], 
           [160, 120, 200, 255], [140, 100, 180, 255], [120, 80, 160, 255], [100, 60, 140, 255], [80, 40, 120, 255], [60, 20, 100, 255], 
           [40, 0, 80, 255], [20, 0, 60, 255], [100, 164, 228, 255], [92, 156, 220, 255], [84, 148, 212, 255], [76, 140, 204, 255], 
           [68, 132, 196, 255], [60, 124, 188, 255], [52, 116, 180, 255], [44, 108, 172, 255], [36, 100, 164, 255], [28, 92, 156, 255], 
           [20, 84, 148, 255], [12, 76, 140, 255], [4, 68, 132, 255], [0, 60, 124, 255], [0, 52, 116, 255], [0, 44, 108, 255], 
           [228, 60, 0, 255], [228, 84, 0, 255], [228, 108, 0, 255], [228, 132, 0, 255], [228, 156, 0, 255], [228, 180, 0, 255], 
           [228, 204, 0, 255], [228, 228, 0, 255], [228, 60, 0, 255], [228, 84, 0, 255], [228, 108, 0, 255], [228, 132, 0, 255], 
           [228, 156, 0, 255], [228, 180, 0, 255], [228, 204, 0, 255], [228, 228, 0, 255], [228, 148, 124, 255], [204, 132, 108, 255], 
           [188, 112, 96, 255], [172, 96, 80, 255], [224, 140, 92, 255], [208, 128, 96, 255], [192, 120, 88, 255], [176, 108, 76, 255], 
           [112, 72, 72, 255], [120, 80, 80, 255], [128, 88, 88, 255], [136, 96, 96, 255], [144, 104, 104, 255], [152, 112, 112, 255], 
           [160, 120, 120, 255], [168, 128, 128, 255]]
#screen.set_palette(palette) #needed if changing the display palette
#pygame.display.set_palette(palette)
tile.set_palette(palette)

#f = open('palette', 'w')
#print>>f, palette

palette = list(palette)

def paletteShift(palette):
	start = 224
	palette[start:start+16] = cycleList(palette[start:start+16])
	return palette
	
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
	
counter = 1
while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			palette = paletteShift(palette)
			#pygame.display.set_palette(palette)
			tile.set_palette(palette)
			print "Palette Shift " + str(counter)
			counter += 1 
	screen.fill(black)
	screen.blit(tile, (0,0))
	pygame.display.flip()

