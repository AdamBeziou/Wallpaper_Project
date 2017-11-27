import sys
import BackChange
import PicPicker
import threading		#Used for letting the GUI still run while new events are scheduled
import wx				#Used for the GUI
import time				#Used for determining when to switch wallpapers
import sched			#Used to scheduling new events to switch wallpapers
import os				#Used pretty much everywhere


def Preview(profile):
	#Function for showing a preview of a chosen image, ending either with a return to the MainWindow or a recursive function call
	
	class YesNo(wx.Dialog):
		def __init__(self):
			wx.Dialog.__init__(self, None, id = wx.ID_ANY, title = "If you see this, something is broken.", style = wx.MAXIMIZE)
	
			self.panel = wx.Panel(self)
			
			scale = wx.DisplaySize()
			bmp = wx.Image(result, wx.BITMAP_TYPE_ANY).Scale(scale[0], scale[1]).ConvertToBitmap()
			self.bitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
			
			self.prompt = wx.StaticText(self.bitmap, label = "Add the Wallpaper to the Current Profile?", pos = (40,20))
		
			self.yes_button = wx.Button(self.bitmap, wx.ID_ANY, "Yes", size = (-1,-1), pos = (55,40))
			self.no_button = wx.Button(self.bitmap, wx.ID_ANY, "No", size = (-1,-1), pos = (155,40))
			self.Bind(wx.EVT_BUTTON, self.OnYes, self.yes_button)
			self.Bind(wx.EVT_BUTTON, self.OnNo, self.no_button)
		
			self.box = wx.StaticBox(self.bitmap, wx.ID_ANY, pos = (5,0), size = (300, 75))
			
			self.ShowFullScreen(True)
	
		def OnYes(self, event):
			config = open("Profiles\\" + profile, 'r').read()
			config = config.splitlines()
			directory = config[0]
			file_name = result.split('\\').pop()
			os.rename(result, directory + '\\' + file_name)
			self.Destroy()
		
		def OnNo(self, event):
			self.Destroy()
	
	dlg = wx.FileDialog(None, "Choose an Image:", style = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
	cancel = dlg.ShowModal()
	result = dlg.GetPath()
	dlg.Destroy()
	
	if cancel == wx.ID_CANCEL:
		return
		
	else:
		dlg1 = YesNo()
		dlg1.ShowModal()
		Preview(profile)
	

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		
		#Initial selection of a profile
		profile_list = os.listdir("Profiles")
		if profile_list == []:
			dlg = wx.TextEntryDialog(None, "Enter the name of your new profile:", "Name the New Profile", style = wx.OK)
			dlg.ShowModal()
			name = dlg.GetValue()
			dlg.Destroy()
			dlg = wx.DirDialog(None, "Choose your wallpaper directory:", style = wx.DD_DEFAULT_STYLE)
			dlg.ShowModal()
			dir = dlg.GetPath()
			dlg.Destroy()
			dlg = wx.TextEntryDialog(parent, message = "Enter the frequency of background changes in seconds: ", caption = "Set Frequency", style = wx.OK)
			dlg.ShowModal()
			freq = dlg.GetValue()
			dlg.Destroy()
			created_profile = open("Profiles\\" + name + ".txt", 'w+')
			created_profile.write(dir + "\n")
			created_profile.write(freq)
			created_profile.close()
			self.profile = name + ".txt"
		else:
			self.select_profile = wx.SingleChoiceDialog(parent, "Select a Profile Below:", "Select a Profile", profile_list, style=wx.OK)
			self.select_profile.ShowModal()
			self.profile = self.select_profile.GetStringSelection()
		
		#Setting up and getting the frequency/directory from a profile
		config = open("Profiles\\" + self.profile, 'r').read()
		config = config.splitlines()
		frequency = config[1]
		directory = config[0]
		wx.Frame.__init__(self, parent, title=title, size=(1000,400), style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
			
		#Setting the background color
		self.SetBackgroundColour(wx.Colour(209,209,209))
		
		#Creating a status bar
		self.CreateStatusBar()
		
		#Creating, appending items to, and binding events to a menu
		menu = wx.Menu()
		changeprofile = menu.Append(wx.ID_ANY, "Change Profile", "Change the Current Profile")
		new_profile = menu.Append(wx.ID_ANY, "Create a New Profile", "Create a New Profile")
		changepath = menu.Append(wx.ID_ANY, "Change Path for this Profile", "Change the Directory for the Wallpapers")
		changefrequency = menu.Append(wx.ID_ANY, "Change Frequency for this Profile", "Change How Often Wallpapers are Changed")
		self.Bind(wx.EVT_MENU, self.OnPath, changepath)
		self.Bind(wx.EVT_MENU, self.OnCreateNewProfile, new_profile)
		self.Bind(wx.EVT_MENU, self.OnFrequency, changefrequency)
		self.Bind(wx.EVT_MENU, self.OnNewProfile, changeprofile)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.menuBar = wx.MenuBar()
		self.menuBar.Append(menu, "Options")
		self.SetMenuBar(self.menuBar)
		
		#Setting up and adding things to the panel
		self.panel = wx.Panel(self)
		
		self.description = wx.StaticText(self.panel, label="Wallpaper Switcher")
		self.description.Wrap(150)
		
		self.profile_name = wx.StaticText(self.panel, label="Profile: "+ self.profile)
		self.profile_name.Wrap(150)
		
		shown_path = directory.split('\\')
		self.path = wx.StaticText(self.panel, label="Path: " + '...' + '\\'.join(shown_path[-3:]))
		self.path.Wrap(150)
		
		self.frequency = wx.StaticText(self.panel, label="Frequency: " + frequency + " Seconds.")
		self.frequency.Wrap(150)
			
		self.start_button = wx.ToggleButton(self.panel, wx.ID_ANY, "Start Cycling Wallpapers", size = (160,50))
		self.Bind(wx.EVT_TOGGLEBUTTON, self.OnButton, self.start_button)
		
		self.change_button = wx.Button(self.panel, wx.ID_ANY, "Manually Change Wallpaper", size = (160,50))
		self.Bind(wx.EVT_BUTTON, self.OnChangeButton, self.change_button)

		self.frequency_button = wx.Button(self.panel, wx.ID_ANY, "Change Frequency", size = (160,50))
		self.Bind(wx.EVT_BUTTON, self.OnFrequency, self.frequency_button)
		
		self.path_button = wx.Button(self.panel, wx.ID_ANY, "Change Path", size = (160,50))
		self.Bind(wx.EVT_BUTTON, self.OnPath, self.path_button)
		
		self.preview_button = wx.Button(self.panel, wx.ID_ANY, "Preview and Add New Wallpapers to the Current Profile")
		self.Bind(wx.EVT_BUTTON, self.OnPreviewButton, self.preview_button)
		
		self.icon = wx.StaticBitmap(self.panel, wx.ID_ANY)
		self.icon.SetBitmap(wx.Bitmap('Untitled.bmp'))
		
		#Setting up a vertical sizer
		self.grid_sizer = wx.GridBagSizer(hgap = 5, vgap = 5)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer_top = wx.BoxSizer(wx.HORIZONTAL)
		
		self.sizer_top.Add(self.icon, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
		self.sizer_top.Add((10,0), 0)
		self.sizer_top.Add(self.description, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
		
		self.grid_sizer.Add(self.start_button, pos=(0,0))
		self.grid_sizer.Add(self.change_button, pos=(1,0))
		self.grid_sizer.Add(self.frequency_button, pos=(2,0))
		self.grid_sizer.Add(self.path_button, pos=(3,0))
		self.grid_sizer.Add(self.profile_name, pos=(1,2), flag=wx.ALIGN_CENTER_HORIZONTAL)
		self.grid_sizer.Add(self.path, pos=(2,2), flag=wx.ALIGN_CENTER_HORIZONTAL)
		self.grid_sizer.Add(self.frequency, pos=(3,2), flag=wx.ALIGN_CENTER_HORIZONTAL)
		
		self.sizer.Add(self.sizer_top, 0 , wx.CENTER, 5)
		self.sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
		self.sizer.Add((0,10), 0)
		self.sizer.Add(self.grid_sizer, 1, wx.ALL|wx.CENTER, 5)
		self.sizer.Add((0,10), 0)
		self.sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
		self.sizer.Add((0,10), 0)
		self.sizer.Add(self.preview_button, 0, wx.CENTER, 5)
		self.sizer.Add((0,10), 0)

		self.sizer.SetSizeHints(self)
		self.SetSizer(self.sizer)
	
		#Setting the frame to appear
		self.Show(True)
			
	def OnPath(self, event):
		#Change path for the current profile, uses the ChangePath() function
		new_config = ChangePath(self.profile, message = "Choose the Wallpaper Folder:")
		shown_path = new_config[0].split('\\')
		self.path.SetLabel("Path: " + '...' + '\\'.join(shown_path[-2:]))
		self.path.Wrap(150)
		config = open("Profiles\\" + self.profile, 'w')
		config.truncate()
		config.write(new_config[0] + "\n")
		config.write(new_config[1])
		config.close()
		
	def OnFrequency(self, event):
		#Change frequency for the current profile, uses the ChangeFrequency() function
		new_config = ChangeFrequency(self.profile, message = "Enter the frequency of background changes in seconds: ", caption = "Set Frequency")
		self.frequency.SetLabel("Frequency: " + new_config[1] + " Seconds.")
		self.frequency.Wrap(150)
		config = open("Profiles\\" + self.profile, 'w')
		config.truncate()
		config.write(new_config[0] + "\n")
		config.write(new_config[1])
		config.close()
		
	def OnNewProfile(self, event):
		#Select a new profile from a list of profiles
		profile_list = os.listdir("Profiles")
		self.select_profile = wx.SingleChoiceDialog(parent = None, message="Select a Profile Below:", caption="Select a Profile", choices = profile_list, style=wx.OK)
		self.select_profile.ShowModal()
		self.profile = self.select_profile.GetStringSelection()
		
		config = open("Profiles\\" + self.profile, 'r').read()
		config = config.splitlines()
		frequency = config[1]
		directory = config[0]
		
		self.profile_name.SetLabel("Profile: "+ self.profile)
		self.profile_name.Wrap(150)
		self.path.SetLabel("Path: " + directory)
		self.path.Wrap(150)
		self.frequency.SetLabel("Frequency: " + frequency + " Seconds.")
		self.frequency.Wrap(150)
		
	def OnCreateNewProfile(self, event):
		#Create a new profile, setting a name, path, and frequency
		dlg = wx.TextEntryDialog(None, "Enter the name of your new profile:", "Name the New Profile", style = wx.OK)
		dlg.ShowModal()
		name = dlg.GetValue()
		dlg.Destroy()
		dir_list = ChangePath(self.profile, message = "Choose the Wallpaper Folder:")
		freq_list = ChangeFrequency(self.profile, message = "Enter the frequency of background changes in seconds: ", caption = "Set Frequency")
		created_profile = open("Profiles\\" + name + ".txt", 'w+')
		created_profile.write(dir_list[0] + "\n")
		created_profile.write(freq_list[1])
		created_profile.close()
		
		#self.path = wx.StaticText(self.panel, label="Path: " + '...' + '\\'.join(shown_path[-3:]))
		self.profile = name + '.txt'
		self.profile_name.SetLabel("Profile: "+ self.profile)
		self.profile_name.Wrap(150)
		shown_path = dir_list[0].split('\\')
		self.path.SetLabel("Path: " + '...' + '\\'.join(shown_path[-3:]))
		self.path.Wrap(150)
		self.frequency.SetLabel("Frequency: " + freq_list[1] + " Seconds.")
		self.frequency.Wrap(150)
		
	def OnButton(self, event):
		#Starts a new thread with a repeating scheduler which repeatedly changes the computer's wallpaper every x number of seconds
		config = open("Profiles\\" + self.profile, 'r').read()
		config = config.splitlines()
		directory = config[0]
		frequency = int(config[1])
		self.menuBar.EnableTop(0, False)
		self.change_button.Disable()
		self.frequency_button.Disable()
		self.path_button.Disable()
		self.start_button.SetLabel("Stop")
		
		def Scheduler(directory, frequency):
			s = sched.scheduler(time.time, time.sleep)
			def CHANGE(directory, frequency):
				if self.start_button.GetValue() == True:
					file_used = ''
					file = PicPicker.PicPicker(directory, file_used)
					final_path = directory + "\\" + file
					BackChange.BackChange(final_path)
					file_used = file
					s.enter(frequency, 1, CHANGE, (directory, frequency))
				else:
					self.menuBar.EnableTop(0, True)
					self.start_button.SetLabel("Start Cycling Wallpapers")
					return
			s.enter(frequency, 1, CHANGE, (directory, frequency))
			while self.start_button.GetValue() == True:
				s.run()
			else:
				self.start_button.SetLabel("Start Cycling Wallpapers")
				self.menuBar.EnableTop(0, True)
				self.change_button.Enable()
				self.frequency_button.Enable()
				self.path_button.Enable()
				return
		
		t = threading.Thread(target=Scheduler, args = (directory, frequency))
		t.start()
		
	def OnChangeButton(self, event):
		dlg = wx.FileDialog(self, message = "Choose a Wallpaper:", style = wx.FD_OPEN)
		choice = dlg.ShowModal()
		if choice == wx.ID_OK:
			result = dlg.GetPath()
			BackChange.BackChange(result)
		dlg.Destroy()
	
	def OnPreviewButton(self, event):
		#Runs the "Preview" function, displaying a selected wallpaper for preview
		Preview(self.profile)

	def OnClose(self, event):
		#Destroys all running threads
		try:
			self.select_profile.Destroy()
			self.Destroy()
		except AttributeError:
			self.Destroy()
	
def ChangePath(profile, parent = None, message = '', caption = ''):
	#Function for changing a path
	config = open("Profiles\\" + profile, 'r').read()
	config = config.splitlines()
	directory = config[0]
	frequency = config[1]
	dlg = wx.DirDialog(parent, message, defaultPath = directory, style = wx.DD_DEFAULT_STYLE)
	dlg.ShowModal()
	result = dlg.GetPath()
	dlg.Destroy()
	new_config = [result, frequency]
	return new_config
	
def ChangeFrequency(profile, parent = None, message = '', caption = ''):
	#Function for changing frequency
	
	class FrequencyInput(wx.Dialog):
		def __init__(self):
			wx.Dialog.__init__(self, None, id = wx.ID_ANY, title = "Frequency:", style = wx.STAY_ON_TOP)
		
			self.panel = wx.Panel(self)
		
			self.prompt = wx.StaticText(self.panel, label = "Enter the frequency of background changes in seconds:")
			
			self.input = wx.TextCtrl(self.panel, wx.ID_ANY, value = frequency, style = wx.TE_PROCESS_ENTER)
			self.input.Bind(wx.EVT_CHAR, self.OnInput)
			
			self.ok = wx.Button(self.panel, wx.ID_OK, "OK", size = (-1,-1))
			self.cancel = wx.Button(self.panel, wx.ID_ANY, "Cancel", size = (-1,-1))
			#self.Bind(wx.EVT_BUTTON, self.OnOk, self.ok)
			self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)
			
			self.sizer = wx.BoxSizer(wx.HORIZONTAL)
			self.over_sizer = wx.BoxSizer(wx.VERTICAL)
			self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
			
			self.bottom_sizer.Add(self.ok, 0, wx.ALL, 5)
			self.bottom_sizer.Add(self.cancel, 0, wx.ALL, 5)
			
			self.over_sizer.Add(self.prompt, 0, wx.CENTER, 5)
			self.over_sizer.Add(self.input, 0, wx.EXPAND|wx.CENTER, 5)
			self.over_sizer.Add(self.bottom_sizer, 0, wx.CENTER, 5)
			
			self.sizer.Add((10,0), 0)
			self.sizer.Add(self.over_sizer, 0, wx.ALL, 5)
			self.sizer.Add((10,0), 0)
			
			self.sizer.SetSizeHints(self)
			self.SetSizer(self.sizer)
		
		#def OnOk(self, event):
			#self.frequency = self.input.GetValue()
			#self.Destroy()
			
		def OnCancel(self, event):
			self.Destroy()
			
		def OnInput(self, event):
			approved = "0123456789"
			key = event.GetKeyCode() 
			if chr(key) in approved or key == 13 or key == 314 or key == 316 or key == 8:
				event.Skip()
				return
				
			else:
				return False
				
	config = open("Profiles\\" + profile, 'r').read()
	config = config.splitlines()
	directory = config[0]
	frequency = config[1]
	dlg = FrequencyInput()
	choice = dlg.ShowModal()
	
	if choice == wx.ID_OK:
		frequency = dlg.input.GetValue()
		
	dlg.Destroy()
	new_config = [directory, frequency]
	return new_config

#Starts the application
app = wx.App(False)
frame = MainWindow(None, "Wallpaper Switcher")
app.MainLoop()