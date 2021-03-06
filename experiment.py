# -*- coding: utf-8 -*-

__author__ = "Brett Feltmate"

import klibs
from klibs import P
from klibs.KLConstants import STROKE_CENTER, TK_S, NA, RC_KEYPRESS, RECT_BOUNDARY
from klibs.KLUtilities import *
from klibs.KLKeyMap import KeyMap
from klibs.KLUserInterface import any_key, ui_request
from klibs.KLGraphics import fill, blit, flip, clear
from klibs.KLGraphics.KLDraw import *
from klibs.KLResponseCollectors import *
from klibs.KLEventInterface import TrialEventTicket as ET
from klibs.KLCommunication import message
from klibs.KLExceptions import TrialException
from klibs.KLTime import Stopwatch, CountDown, precise_time

# Import required external libraries
import sdl2
import time
import random
import math

# Define some useful constants
SPACE 	= "space"
TIME 	= "time"
HOMO 	= "homo"
HETERO 	= "hetero"
PRESENT = "present"
ABSENT 	= "absent"
BLACK 	= (0,0,0,255)
WHITE 	= (255,255,255,255)


class SSAT_line(klibs.Experiment):

	def setup(self):
		self.group = random.choice(['A','B'])
		# Stimulus sizes
		fix_size            = deg_to_px(0.6)
		fix_thickness       = deg_to_px(0.1)
		self.item_size      = deg_to_px(0.8)
		self.item_thickness = deg_to_px(.1)

		# Initilize drawbjects
		self.fixation = FixationCross(fix_size, fix_thickness, fill=WHITE)
		
		# Initialize ResponseCollectors
		self.spatial_rc  		= ResponseCollector(uses=RC_KEYPRESS)
		self.temporal_pre_rc 	= ResponseCollector(uses=RC_KEYPRESS, flip_screen=True)
		self.temporal_post_rc 	= ResponseCollector(uses=RC_KEYPRESS, flip_screen=True)

		self.group_A_keymap = KeyMap("search_response", ['z','/'], ['absent','present'], [sdl2.SDLK_z, sdl2.SDLK_SLASH])
		self.group_B_keymap = KeyMap("search_response", ['z','/'], ['present','absent'], [sdl2.SDLK_z, sdl2.SDLK_SLASH])

		self.item_duration = .1 # seconds
		self.isi = .05  		# seconds


		self.anykey_text = "{0}\nPress any key to continue."

		self.group_A_instuctions 		= "If you see the target item, please press the '/' key.\nIf you don't see the target item, please press the 'z' key."
		self.group_B_instuctions 		= "If you see the target item, please press the 'z' key.\nIf you don't see the target item, please press the '/' key."

		self.general_instructions_1 	= "In this experiment, you will see a series of items; amongst these items a target item may, or may not, be presented.\n{0}"
		self.general_instructions_2 	= self.general_instructions_1.format(self.group_A_instuctions if self.group == "A" else self.group_B_instuctions)
		self.general_instructions_3 	= ("{0}\nThe experiment will begin with a few practice rounds to familiarlize yourself with the task."
									   	"\n\nBefore every trial, a preview of the target item will be presented.")

		self.spatial_instructions_1	 	= "Searching in Space!\n\nFor these trials, you will see a collection of items arranged in a circle.\n{0}"
		self.temporal_instructions_1 	= "Searching in Time!\n\nFor these trials, you will see a series of items presented one at a time, center screen.\n{0}"
		
		self.group_A_spatial 			= ("If one of the items is the target, press the '/' key as fast as possible.\n"
							    		"If none of the items are the target, press the 'z' key as fast as possible.")

		self.group_B_spatial 			= ("If one of the items is the target, press the 'z' key as fast as possible.\n"
							    		"If none of the items are the target, press the '/' key as fast as possible.")

		self.group_A_temporal 			= ("At any time, if you see the target item, press the '/' key as fast as possible.\n"
								 		"Once the images stop appearing, if you haven't seen the target item, press the 'z' key as fast as possible.")
		
		self.group_B_temporal 			= ("At any time, if you see the target item, press the 'z' key as fast as possible.\n"
								 		"Once the images stop appearing, if you haven't seen the target item, press the '/' key as fast as possible.")

		self.general_instructions 		= self.general_instructions_3.format(self.general_instructions_2)
		self.spatial_instructions 		= self.spatial_instructions_1.format(self.group_A_spatial if self.group == 'A' else self.group_B_spatial)
		self.temporal_instructions 		= self.temporal_instructions_1.format(self.group_A_temporal if self.group == 'A' else self.group_B_temporal)

		self.general_instruct_shown 	= False

		self.spatial_conditions_exp 	= [[HOMO, HETERO], [HOMO, HOMO], [HETERO, HOMO], [HETERO, HETERO]]
		self.temporal_conditions_exp 	= [[HOMO, HETERO], [HOMO, HOMO], [HETERO, HOMO], [HETERO, HETERO]]

		self.practice_conditions 		= [[HETERO, HOMO], [HETERO, HETERO], [HOMO, HETERO], [HOMO, HOMO]]

		random.shuffle(self.spatial_conditions_exp)
		random.shuffle(self.temporal_conditions_exp)
		random.shuffle(self.practice_conditions)


		self.search_type = random.choice([SPACE,TIME])

		if P.run_practice_blocks:
			self.insert_practice_block(block_nums=range(1,5), trial_counts=P.trials_per_practice_block)

	def block(self):
		if not P.practicing:
			if self.search_type == SPACE:
				self.condition = self.spatial_conditions_exp.pop()
			else:
				self.condition = self.temporal_conditions_exp.pop()
		else:
			self.condition = self.practice_conditions.pop()

		self.target_distractor, self.distractor_distractor = self.condition

		self.target_tilt = random.randint(0,179)
		self.target_item = Rectangle(self.item_size, self.item_thickness, fill=WHITE, rotation=self.target_tilt)

		self.create_stimuli()

		if not self.general_instruct_shown:
			self.general_instruct_shown = True
			
			general_text = self.anykey_text.format(self.general_instructions)
			general_msg  = message(general_text, align='left',blit_txt=False)

			fill()
			blit(general_msg,5, P.screen_c)
			flip()
			any_key()

		block_txt 		= "Block {0} of {1}".format(P.block_number, P.blocks_per_experiment)
		progress_txt 	= self.anykey_text.format(block_txt)

		if P.practicing:
			progress_txt += "\n(This is a practice block)"

		progress_msg 	= message(progress_txt, align='center', blit_txt=False)

		fill()
		blit(progress_msg,5,P.screen_c)
		flip()
		any_key()

		if self.search_type == SPACE:
			block_type_txt = self.anykey_text.format(self.spatial_instructions)
		else:
			block_type_txt = self.anykey_text.format(self.temporal_instructions)

		block_type_msg = message(block_type_txt, align='left', blit_txt=False)

		fill()
		blit(block_type_msg, 5, P.screen_c)
		flip()
		any_key()

	def setup_response_collector(self):
		self.spatial_rc.terminate_after 					= [10, TK_S]
		self.spatial_rc.keypress_listener.interrupts 		= True
		self.spatial_rc.keypress_listener.key_map 			= self.group_A_keymap if self.group == 'A' else self.group_B_keymap

		self.temporal_pre_rc.terminate_after 				= [10, TK_S]
		self.temporal_pre_rc.keypress_listener.key_map 		= self.group_A_keymap if self.group == 'A' else self.group_B_keymap
		self.temporal_pre_rc.keypress_listener.interrupts 	= True 
		self.temporal_pre_rc.display_callback 				= self.present_stream
		
		self.temporal_post_rc.terminate_after 				= [5, TK_S]
		self.temporal_post_rc.keypress_listener.key_map 	= self.group_A_keymap if self.group == 'A' else self.group_B_keymap
		self.temporal_post_rc.keypress_listener.interrupts  = True 
		self.temporal_post_rc.display_callback 				= self.post_stream

	def trial_prep(self):
		self.target_onset = NA

		if self.search_type == SPACE:
			array_radius = deg_to_px(8)
			theta = 360.0 / self.set_size

			self.item_locs = []

			for i in range(0, self.set_size):
				self.item_locs.append(point_pos(origin=P.screen_c, amplitude=array_radius, angle=0, rotation=theta*(i+1)))

			random.shuffle(self.item_locs)
			if self.present_absent == PRESENT:
				self.target_loc = self.item_locs.pop()

		else:
			self.rsvp_stream = self.prepare_stream()
			self.rsvp_stream.reverse() # items are extracted via pop() in present_stream() 


		events = [[1000, 'present_target']]
		events.append([events[-1][0] + 1000, 'present_fixation'])
		events.append([events[-1][0] + 1000, 'search_onset'])
		
		for e in events:
			self.evm.register_ticket(ET(e[1], e[0]))

		hide_mouse_cursor()
		self.present_target()

	def trial(self):
		# Wait 1s before presenting array
		while self.evm.before("present_fixation", True):
			ui_request()

		self.present_fixation()

		while self.evm.before("search_onset", True):
			ui_request()
		
		
		if self.search_type == SPACE:
			self.present_array()
			self.spatial_rc.collect()

			if len(self.spatial_rc.keypress_listener.responses):
				spatial_response, spatial_rt = self.spatial_rc.keypress_listener.response()
				
				if spatial_response != self.present_absent:
					self.present_feedback()
			else:
				spatial_response = "None"
				spatial_rt 		 = 'NA'
		else:

			try:
				self.response_sw = Stopwatch() # Used as RT stopwatch in cases where responses are made after stream has ended
				self.stream_sw   = Stopwatch()	# Records duration of stream, just in case it becomes handy to have
				self.target_sw   = Stopwatch()	# Records time that target is presented, again just in case.

				# the display callback "present_stream()" pops an element each pass; when all targets have been shown this bad boy throws an error
				self.temporal_pre_rc.collect()
			except IndexError:
				pass
			
			# Pause once stream has ended
			self.stream_sw.pause()

			if len(self.temporal_pre_rc.keypress_listener.responses):
				temporal_response, temporal_rt = self.temporal_pre_rc.keypress_listener.response()

			else:
				self.temporal_post_rc.collect()

				if len(self.temporal_post_rc.keypress_listener.responses):
					temporal_rt 	  = self.response_sw.elapsed() * 1000 # Rescale RT to ms and log
					temporal_response = self.temporal_post_rc.keypress_listener.response(rt=False)

				else:
					temporal_response = "None"
					temporal_rt 	  = "NA"

			if temporal_response != self.present_absent:
				self.present_feedback()
		
		clear()

		return {
			"practicing": 				str(P.practicing),
			"block_num": 				P.block_number,
			"trial_num": 				P.trial_number,
			"search_type": 				self.search_type,
			"stimulus_type": 			'LINE',
			"present_absent": 			self.present_absent,
			"set_size": 				self.set_size if self.search_type == SPACE else 'NA',
			"target_distractor": 		self.target_distractor,
			"distractor_distractor": 	self.distractor_distractor,
			"target_time": 				self.target_time if self.search_type == TIME else "NA",
			"stream_duration": 			self.stream_sw.elapsed() if self.search_type == TIME else "NA",
			"target_onset": 			self.target_onset if self.search_type == TIME else "NA",
			"spatial_response": 		spatial_response if self.search_type == SPACE else "NA",
			"spatial_rt": 				spatial_rt if self.search_type == SPACE else "NA",
			"temporal_response": 		temporal_response if self.search_type == TIME else "NA",
			"temporal_rt": 				temporal_rt if self.search_type == TIME else "NA"
		}


	def trial_clean_up(self):
		self.spatial_rc.keypress_listener.reset()
		self.temporal_pre_rc.keypress_listener.reset()
		self.temporal_post_rc.keypress_listener.reset()

		if not P.practicing:
			if P.trial_number == P.trials_per_block:
				if self.search_type == SPACE:
					self.search_type = TIME
				else:
					self.search_type = SPACE
		else:
			if P.trial_number == P.trials_per_practice_block:
				if self.search_type == SPACE:
					self.search_type = TIME
				else:
					self.search_type = SPACE

	def clean_up(self):
		pass

	def present_target(self):
		msg = "This is your target!"
		msg_loc = [P.screen_c[0], (P.screen_c[1] - deg_to_px(2))]

		fill()
		message(msg, location=msg_loc, registration=5)
		blit(self.target_item, location=P.screen_c, registration=5)
		flip()

	def present_fixation(self):
		fill()
		blit(self.fixation, location=P.screen_c, registration=5)
		flip()

	def present_feedback(self):
		fill()
		message("Incorrect!", location=P.screen_c, registration=5, blit_txt=True)
		flip()

		feedback_period_cd = CountDown(0.5) # seconds
		while feedback_period_cd.counting():
			ui_request()

	def create_stimuli(self):
		ref_angle = self.target_tilt if self.target_distractor == HOMO else self.target_tilt + 90

		self.distractor_tilts = []

		if self.distractor_distractor == HOMO:
			pad = random.choice([-20,20])
			self.distractor_tilts.append(ref_angle + pad)

		else:
			for i in range(1,3):
				self.distractor_tilts.append(ref_angle + (20*i))
				self.distractor_tilts.append(ref_angle - (20*i))

		self.distractors = []
		
		for t in self.distractor_tilts:
			self.distractors.append(Rectangle(self.item_size, self.item_thickness, fill=WHITE, rotation=t))

	def present_array(self):
		fill()
		blit(self.fixation, registration=5, location=P.screen_c)
		
		if self.present_absent == PRESENT:
			blit(self.target_item, registration=5, location=self.target_loc)
	
		for loc in self.item_locs:
			blit(random.choice(self.distractors), registration=5, location=loc)
		
		flip()

	def prepare_stream(self):
		self.stream_length = 16

		stream_items = []

		if self.present_absent == PRESENT:
			self.target_time = random.randint(5, 12)
		else:
			self.target_time = -1

		for i in range(self.stream_length):
			if i == self.target_time:
				stream_items.append([self.target_item, True])
			else:
				stream_items.append([random.choice(self.distractors), False])

		return stream_items
	

	def present_stream(self):

		duration_cd = CountDown(self.item_duration, start=False)
		isi_cd = CountDown(self.isi, start=False)

		item = self.rsvp_stream.pop()
		
		fill()
		blit(item[0], registration=5, location=P.screen_c)
		flip()

		duration_cd.start()
		while duration_cd.counting():
			pass
		
		fill()

		if item[1]:
			self.target_onset = self.target_sw.elapsed()
		
		isi_cd.start()
		while isi_cd.counting():
			pass


	def post_stream(self):
		fill()
		flip()