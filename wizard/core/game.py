# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module manages the wizard "game" part
# it uses the "site" module to access 
# and write user data
# Uses this module to add xps, levels,
# remove levels and remove life

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

from wizard.core import site
from wizard.core import environment

def add_xps(amount):
	# Add the amount of xps to the user
	# if the xp amount gets to 100,
	# the user win 1 level and the xps
	# get back to 0
	user_row = site.get_user_row_by_name(environment.get_user())
	new_total_xp = user_row['total_xp'] + amount
	new_xp = user_row['xp'] + amount
	if new_xp >= 100:
		new_xp -= 100
		add_levels(1)
	site.modify_user_xp(user_row['user_name'], new_xp)
	site.modify_user_total_xp(user_row['user_name'], new_total_xp)

def add_levels(amount):
	user_row = site.get_user_row_by_name(environment.get_user())
	new_level = user_row['level'] + amount
	site.modify_user_level(user_row['user_name'], new_level)

def remove_levels(amount):
	user_row = site.get_user_row_by_name(environment.get_user())
	new_level = user_row['level'] - amount
	if new_level <= 0:
		new_level = 0
	site.modify_user_level(user_row['user_name'], new_level)

def remove_life(amount):
	# Remove the given amount of life of
	# the current user
	# If the life is 0% or less,
	# the user loose 2 levels and
	# the life get back to 100%
	user_row = site.get_user_row_by_name(environment.get_user())
	new_life = user_row['life'] - amount
	if new_life <= 0:
		new_life = 100
		remove_levels(2)
	site.modify_user_life(user_row['user_name'], new_life)

def analyse_comment(comment, life_amount):
	# Analyse if a comment length is 10 characters 
	# minimum, if not, removes life_amount from the user
	if len(comment) < 10:
		remove_life(life_amount)
		logger.info(f"Warning, bad commenting just made you loose {life_amount}% of life")