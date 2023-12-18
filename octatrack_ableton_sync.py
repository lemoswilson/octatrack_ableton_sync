import Live
from _Framework.ControlSurface import ControlSurface
from _Framework import Task
from ableton.v2.base import task
import uuid

PCC_KEY = "OT PCC"
PCA_KEY = "OT PCA"
IPCS_KEY = "OT IPCS"
QUANTIZATION_SETTING = 5 # 1 Bar

class octatrack_ableton_sync(ControlSurface):
	def __init__(self, c_instance):
		super(octatrack_ableton_sync, self).__init__(c_instance)

		with self.component_guard():
			# Store index keys
			self.pcc_key = PCC_KEY
			self.pca_key = PCA_KEY
			self.ipcs_key = IPCS_KEY
			self.pcc_clip_ids = []
			
			# Set up overarching clip settings
			self.quantization = QUANTIZATION_SETTING

			# Find indexes
			self.find_indexes()

			# Setup listeners
			self.song().add_tracks_listener(self.find_indexes)
			self.add_clip_slots_listeners()
			# self.add_scenes_listener(self.scenes_listener_handler)

	def defer(self, *tasks):
		tasks = [Task.delay(1)] + list(map(lambda x: Task.run(x), tasks))
		self._tasks.add(Task.sequence(*tasks))

	def log(self, *messages):
		self.log_message("csslog: ", *messages)

	# Find indexes for OT handling tracks
	def find_indexes(self):
		self.pcc_index = self.find_pcc_index()
		self.pca_index = self.find_pca_index()
		self.ipcs_index = self.find_ipcs_index()

	# Find the index of a track given its name
	def find_index_of(self, track_name):
		for index, track in enumerate(self.song().tracks):
			if track.name == track_name: return index

	# Get the PCC index
	def find_pcc_index(self): 
		return self.find_index_of(self.pcc_key)

	# Get the PCA index
	def find_pca_index(self):
		return self.find_index_of(self.pca_key)

	# Get the IPCS index
	def find_ipcs_index(self):
		return self.find_index_of(self.ipcs_key)

	# # Remoev and add clip_slots listeners 
	# def scenes_listener_handler(self):
	# 	self.remove_clip_slots_listeners()
	# 	self.add_clip_slots_listeners()

	# # Remove the PCC clip slot listeners
	# def remove_clip_slots_listeners(self):
	# 	for clip_slot in self.song().tracks[self.pcc_index].clip_slots:
	# 		clip_slot.remove_has_clip_listener(self.has_clip_handler(clip_slot))
	# 		clip_slot.remove_is_triggered_listener(self.is_triggered_listener_handler(clip_slot))

	# Set the PCC clip slot listeners
	def add_clip_slots_listeners(self):
		for clip_slot in self.song().tracks[self.pcc_index].clip_slots:
			clip_slot.add_has_clip_listener(self.has_clip_handler(clip_slot))
			clip_slot.add_is_triggered_listener(self.is_triggered_listener_handler(clip_slot))

	# Handle the is_triggered_listener on PCC slots, if user triggers a PCC clip
	# both PCA and IPCS should be triggered/fired as well
	def is_triggered_listener_handler(self, clip_slot):
		def inner():
			self.log("Running is_triggered_listener handler")
			self.log(f"is_triggered? {clip_slot.is_triggered}")
			# # Don't do anything if the clip is not triggered, or there's no trigger
			# if not clip_slot.is_triggered: return
			# if not clip_slot.has_clip: return

			# clip_index = self.get_clip_index(clip_slot.clip, self.pcc_index)

			# song = song()
			# pca_clip = song.tracks[self.pca_index].clip_slots[clip_index]
			# ipcs_clip = song.tracks[self.ipcs_index].clip_slots[clip_index]

			# if not pca_clip.is_triggered and not pca_clip.is_playing:
			# 	pca_clip.fire()

			# if not ipcs_clip.is_triggered and not ipcs_clip.is_playing: 
			# 	pca_clip.fire()

		return inner
		

	# Handle the has_clip listener on PCC slots, if a new clip has been added make sure
	# it has a unique name, and that both PCA and IPCS have a matching clip
	# also reset the notes listener on the clip 
	# If a clip has been removed make sure both PCA and IPCS corresponding clip slots 
	# are also empty
	def has_clip_handler(self, clip_slot):
		def set_clip_name():
			clip_slot.clip.name = str(uuid.uuid4())

		def inner(): 
			if clip_slot.has_clip:
				if not clip_slot.clip.name: self.defer(set_clip_name)

				clip_index = self.get_clip_index(clip_slot.clip, self.pcc_index)

				self.reset_pca_clip_by_index(clip_index)
				self.reset_ipcs_clip_by_index(clip_index)

				self.reset_notes_listener(clip_slot.clip)

				#TODO: PAREI AQUI

				self.reset_loop_listeners(clip_slot.clip)

			else: self.match_empty_clip_slots()

		return inner

	# Reset the looping listeners
	def reset_loop_listeners(self, clip):
		self.reset_loop_end_listener(clip)
		self.reset_end_marker_listener(clip)
		self.reset_looping_listener(clip)

	# Reset the loop_end_listener
	def reset_loop_end_listener(self, clip):
		if clip.loop_end_has_listener(self.loop_end_listener_handler(clip)):
			clip.remove_loop_end_listener(self.loop_end_listener_handler(clip))

		clip.add_loop_end_listener(self.loop_end_listener_handler(clip))


	# Make sure loop_end of PCA and IPCS match PCC's
	def loop_end_listener_handler(self, clip):
		def inner():
			clip_index = self.get_clip_index(clip, self.pcc_index)
			pca_clip = self.song().tracks[self.pca_index].clip_slots[clip_index].clip
			ipcs_clip = self.song().tracks[self.ipcs_index].clip_slots[clip_index].clip

			def deferable():
				pca_clip.loop_end = clip.loop_end
				ipcs_clip.loop_end = clip.loop_end

			self.defer(deferable)

		return inner

	# Reset the end_marker_listener
	def reset_end_marker_listener(self, clip):
		if clip.end_marker_has_listener(self.end_marker_listener_handler(clip)):
			clip.remove_end_marker_listener(self.end_marker_listener_handler(clip))

		clip.add_end_marker_listener(self.end_marker_listener_handler(clip))

	# Make sure end marker of PCA and IPCS match PCC's
	def end_marker_listener_handler(self, clip):
		def inner():
			clip_index = self.get_clip_index(clip, self.pcc_index)
			pca_clip = self.song().tracks[self.pca_index].clip_slots[clip_index].clip
			ipcs_clip = self.song().tracks[self.ipcs_index].clip_slots[clip_index].clip

			def deferable():
				pca_clip.end_marker = clip.end_marker
				ipcs_clip.end_marker = clip.end_marker

			self.defer(deferable)

		return inner

	# Reset the is_looping_listener
	def reset_looping_listener(self, clip):
		if clip.looping_has_listener(self.is_looping_listener_handler(clip)):
			clip.remove_looping_listener(self.is_looping_listener_handler(clip))

		clip.add_looping_listener(self.is_looping_listener_handler(clip))

	# Make sure the PCA is_looping matches PCC's
	def is_looping_listener_handler(self, clip):
		def inner():
			clip_index = self.get_clip_index(clip, self.pcc_index)
			pca_clip = self.song().tracks[self.pca_index].clip_slots[clip_index].clip

			def deferable():
				pca_clip.looping = clip.looping

			self.defer(deferable)

		return inner

	# Reset the notes listener
	def reset_notes_listener(self, clip):
		def deferable():
			if clip.notes_has_listener(self.notes_listener_handler(clip)):
				clip.remove_notes_listener(self.notes_listener_handler(clip))

			clip.add_notes_listener(self.notes_listener_handler(clip))

		self.defer(deferable)

	# Handle the notes_listener, making sure the PCA and IPCS clips
	# are on par with what they should be
	def notes_listener_handler(self, clip):
		def inner(): 
			# get the PCC clip index
			clip_index = self.get_clip_index(clip, self.pcc_index)

			# Get the PCA slot and make its notes
			pca_clip_slot = self.song().tracks[self.pca_index].clip_slots[clip_index]
			pca_notes = self.make_pca_clip_notes_from_pcc_clip(clip)


			# Get the IPCS clip slot and make its notes
			ipcs_clip_slot = self.song().tracks[self.ipcs_index].clip_slots[clip_index]
			ipcs_notes = self.make_ipcs_clip_notes_from_pcc_clip(clip)

			def reset_notes():
				# If PCA already has clip, remove the notes and add again
				if pca_clip_slot.has_clip:
					pca_clip_slot.clip.remove_notes_extended(0, 127, -99999, 99999)
					pca_clip_slot.clip.add_new_notes(pca_notes)

				# If it doesn't create a new clip, and set the clip notes
				else: 
					pca_clip_slot.create_clip(clip.length)
					pca_clip_slot.clip.looping = clip.looping
					pca_clip_slot.clip.launch_quantization = self.quantization # 1 Bar
					pca_clip_slot.clip.add_new_notes(pca_notes)

				# If IPCS already has clip, remove the notes and add again
				if ipcs_clip_slot.has_clip:
					ipcs_clip_slot.clip.remove_notes_extended(0, 127, -99999, 99999)
					ipcs_clip_slot.clip.add_new_notes(ipcs_notes)

				# If it doesn't create a new clip, and set the clip notes
				else:
					ipcs_clip_slot.create_clip(clip.length)
					ipcs_clip_slot.looping = False
					ipcs_clip_slot.launch_quantization = 1 # None
					ipcs_clip_slot.clip.add_new_notes(ipcs_notes)

			self.defer(reset_notes)

		return inner

	# Make sure every IPCS and PCA clip slots are empty, if the corresponding clip slot
	# in the PCC track is empty
	def match_empty_clip_slots(self):
		for index, clip_slot in enumerate(self.song().tracks[self.pcc_index].clip_slots):
			if not clip_slot.has_clip: self.clear_pca_ipcs_clip_slot(index)

	# Delete clip from PCA and IPCS slot given a clip index
	def clear_pca_ipcs_clip_slot(self, index):
		try: self.defer(self.song().tracks[self.pca_index].clip_slots[index].delete_clip)
		except: pass
		try: self.defer(self.song().tracks[self.ipcs_index].clip_slots[index].delete_clip)
		except: pass

	# Get clip_slot index, requires the clip to have a unique name within the its track
	def get_clip_index(self, clip, track_index):
		for index, clip_slot in enumerate(self.song().tracks[track_index].clip_slots):
			if not clip_slot.has_clip: continue 
			elif clip_slot.clip.name == clip.name: return index

	# Get the PCC clip, given its index
	def get_pcc_clip(self, clip_index):
		return self.song().tracks[self.pcc_index].clip_slots[clip_index].clip

	# Make a PCA note given a PCC note
	def make_pca_note_from_pcc_note(self, pcc_note, pcc_clip):
		is_first_note = pcc_note.start_time == 0
		is_looping = pcc_clip.looping
		data = {
			"pitch": pcc_note.pitch,
			"start_time": pcc_clip.length - 3 if is_first_note and is_looping else pcc_note.start_time - 3,
			"duration": pcc_note.duration,
			"velocity": pcc_note.velocity
		}
		return Live.Clip.MidiNoteSpecification(**data)

	# Make PCA clip notes given a PCC clip
	def make_pca_clip_notes_from_pcc_clip(self, pcc_clip):
		notes = pcc_clip.get_notes_extended(0, 127, 0, 99999)
		pca_notes = [self.make_pca_note_from_pcc_note(note, pcc_clip) for note in notes]
		return tuple(pca_notes)

	# Reset the PCA clip of an index, Requires the pcc clip slot of the same index to have a clip
	def reset_pca_clip_by_index(self, index): 
		clip_slot = self.song().tracks[self.pca_index].clip_slots[index]

		if clip_slot.has_clip: clip_slot.delete_clip()

		pcc_clip = self.get_pcc_clip(index)

		def create_clip():
			clip_slot.create_clip(pcc_clip.length)
			clip_slot.clip.looping = pcc_clip.looping
			clip_slot.clip.launch_quantization = self.quantization
			clip_slot.clip.add_new_notes(self.make_pca_clip_notes_from_pcc_clip(pcc_clip))

		self.defer(create_clip)

	# Make IPCS note given a PCC note
	def make_ipcs_note_from_pcc_note(self, pcc_note):
		data = {
			"pitch": pcc_note.pitch,
			"start_time": pcc_note.start_time,
			"duration": pcc_note.duration,
			"velocity": pcc_note.velocity
		}
		return Live.Clip.MidiNoteSpecification(**data)

	# # Make IPCS clip notes based on a PCC clip
	def make_ipcs_clip_notes_from_pcc_clip(self, pcc_clip):
		notes = pcc_clip.get_notes_extended(0, 127, 0, 9999)
		notes = filter(lambda x: x.start_time == 0, notes)
		return tuple([self.make_ipcs_note_from_pcc_note(note) for note in notes])

	# # Reset the IPCS clip of an index, requires the pcc clip slot of the same index to have a clip
	def reset_ipcs_clip_by_index(self, index):
		clip_slot = self.song().tracks[self.ipcs_index].clip_slots[index]

		if clip_slot.has_clip:
			clip_slot.delete_clip()

		pcc_clip = self.get_pcc_clip(index)

		def create_clip():
			clip_slot.create_clip(pcc_clip.length)
			clip_slot.clip.looping = False
			clip_slot.clip.launch_quantization = 1 #
			clip_slot.clip.add_new_notes(self.make_ipcs_clip_notes_from_pcc_clip(pcc_clip))

		self.defer(create_clip)