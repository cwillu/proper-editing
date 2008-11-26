# -*- coding: utf8 -*-
#  Proper editing plugin
# 
#  Copyright (C) 2008 Carey Underwood <cwillu@cwillu.com>
#   
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#   
#  This program is distri hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

import gedit
import gtk

import re
import bisect
import itertools

gtk.rc_parse_string('''binding "nodel" {  
  unbind "<ctrl>Delete"
  unbind "<ctrl>BackSpace"
  unbind "<ctrl><shift>Left"
  unbind "<ctrl><shift>Right"
}class "GtkTextView" binding "nodel"''')

boundary = re.compile(r'''[A-Z]*[a-z]+|\s+|\b|['"_]''')

def getInsertMark(buffer):
  cursor = buffer.get_insert()
  return buffer.get_iter_at_mark(cursor)

def getLine(buffer, mark):
  lineStart = mark.copy()
  lineStart.set_line_offset(0)
  
  lineEnd = mark.copy()
  lineEnd.set_line_offset(lineEnd.get_chars_in_line())
  
  return buffer.get_text(lineStart, lineEnd)
  
def getLineBoundaries(line):
  boundaries = list(itertools.chain(*[m.span() for m in boundary.finditer(line)]))
  if 0 not in boundaries:
    boundaries.insert(0, 0)
  if len(line) not in boundaries:
    boundaries.append(len(line))
  return boundaries

def nextMark(mark, boundaries):
  mark = mark.copy()
  for offset in boundaries:    
    if offset > mark.get_line_offset():
      mark.set_line_offset(offset)
      break
  else:
    offset = mark.get_offset()
    while mark.get_offset() == offset:
      mark.forward_char()    
    
  return mark
  
def previousMark(mark, boundaries):
  mark = mark.copy()
  for offset in boundaries[::-1]:    
    if offset < mark.get_line_offset():
       mark.set_line_offset(offset)
       break
  else:
    mark.backward_cursor_position()      
  return mark

class Actions(gedit.Plugin):
  def Amove_to_next_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    insert = getInsertMark(buffer)
    line = getLine(buffer, insert)
    boundaries = getLineBoundaries(line)
    insert = nextMark(insert, boundaries)
                     
    buffer.place_cursor(insert)
  
  def Amove_to_previous_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    insert = getInsertMark(buffer)
    line = getLine(buffer, insert)
    boundaries = getLineBoundaries(line)
    insert = previousMark(insert, boundaries)
        
    buffer.place_cursor(insert)  

  def Aselect_to_next_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    insert = getInsertMark(buffer)
    line = getLine(buffer, insert)
    boundaries = getLineBoundaries(line)
    insert = nextMark(insert, boundaries)
                     
    buffer.move_mark(buffer.get_insert(), insert)   
  
  def Aselect_to_previous_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    insert = getInsertMark(buffer)
    line = getLine(buffer, insert)
    boundaries = getLineBoundaries(line)
    insert = previousMark(insert, boundaries)
        
    buffer.move_mark(buffer.get_insert(), insert)

  def Adelete_to_next_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    buffer.begin_user_action()
    
    insert = getInsertMark(buffer)
    line = getLine(buffer, insert)
    boundaries = getLineBoundaries(line)
    end = nextMark(insert, boundaries)
                     
    buffer.delete(insert, end)   
    buffer.end_user_action()   
  
  def Adelete_to_previous_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    buffer.begin_user_action()
    
    insert = getInsertMark(buffer)
    line = getLine(buffer, insert)
    boundaries = getLineBoundaries(line)
    end = previousMark(insert, boundaries)
        
    buffer.delete(end, insert)   
    buffer.end_user_action()   
      
def _menu(name):
  return '''<menuitem name="%s" action="%s"/>''' % (name, name)
def _action(operation):
  name = operation.__name__[1:]
  name = name.replace('_', ' ').title()
  return (name, None, name, None, name, operation)

class ProperEditingPlugin(gedit.Plugin):
  def __init__(self):
    gedit.Plugin.__init__(self)
    self.action_object = Actions()
    self.actions = [_action(getattr(self.action_object, a)) for a in dir(self.action_object) if a[0] is 'A']        
    self.adv_edit_str = """
      <ui>
        <menubar name="MenuBar">
          <menu name="EditMenu" action="Edit">
            <placeholder name="ProperOps_7">
              %s
            </placeholder>
          </menu>
        </menubar>
      </ui>
      """ % ''.join([_menu(action[0]) for action in self.actions])
      
  def activate(self, window):
    # store per window data in the window object
    windowdata = dict()
    window.set_data("ProperEditingPluginWindowDataKey", windowdata)

    windowdata["action_group"] = gtk.ActionGroup("GeditProperEditingPluginActions")
    windowdata["action_group"].add_actions(self.actions, window)

    manager = window.get_ui_manager()
    manager.insert_action_group(windowdata["action_group"], -1)

    windowdata["ui_id"] = manager.add_ui_from_string(self.adv_edit_str)
    
    window.set_data("ProperEditingPluginInfo", windowdata)

  def deactivate(self, window):
    windowdata = window.get_data("ProperEditingPluginWindowDataKey")
    manager = window.get_ui_manager()
    manager.remove_ui(windowdata["ui_id"])
    manager.remove_action_group(windowdata["action_group"])

  def update_ui(self, window):
    view = window.get_active_view()
    windowdata = window.get_data("ProperEditingPluginWindowDataKey")
    windowdata["action_group"].set_sensitive(bool(view and view.get_editable()))
