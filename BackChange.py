import ctypes

def BackChange(src):
	SPI_SETDESKWALLPAPER = 0x14
	SPIF_UPDATEINIFILE = 0x2
	ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, src, SPIF_UPDATEINIFILE)
	
if __name__ == '__main__':
    BackChange(src)