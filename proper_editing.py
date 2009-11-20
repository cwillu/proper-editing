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

class weird(object):
  @staticmethod
  def getInsertMark(buffer):
    cursor = buffer.get_insert()
    return buffer.get_iter_at_mark(cursor)

  @staticmethod
  def getSelectionMark(buffer):
    selection = buffer.get_selection_bound()
    return buffer.get_iter_at_mark(selection)

  @staticmethod
  def getLine(buffer, mark):
    lineStart = mark.copy()
    lineStart.set_line_offset(0)
    
    lineEnd = mark.copy()
    lineEnd.set_line_offset(lineEnd.get_chars_in_line())
    
    return buffer.get_text(lineStart, lineEnd)
    
  @staticmethod
  def getLineBoundaries(line):
    boundaries = list(itertools.chain(*[m.span() for m in boundary.finditer(line)]))
    if 0 not in boundaries:
      boundaries.insert(0, 0)
    if len(line) not in boundaries:
      boundaries.append(len(line))
    return boundaries

  @staticmethod
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
    
  @staticmethod
  def previousMark(mark, boundaries):
    mark = mark.copy()
    for offset in boundaries[::-1]:    
      if offset < mark.get_line_offset():
         mark.set_line_offset(offset)
         break
    else:
      mark.backward_cursor_position()      
    return mark

  @staticmethod
  def folded(buffer):
    return buffer.tag_table.lookup('folded')
    
  @staticmethod
  def fold(buffer):
    tag = weird.folded(buffer)
    if not tag:  
      tag = gtk.TextTag("folded")
      tag.set_property('invisible', True)
      tag.set_property('invisible-set', True)
      buffer.tag_table.add(tag)
      
    return tag

class Actions(gedit.Plugin):
  def Afold_from_search(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()

    search, flags = buffer.get_search_text()
    if not search or search == window.get_data("SearchFold")['search']:
      if weird.folded(buffer):
        return self.Aunfold(action, window)
      else:              
        left = weird.getInsertMark(buffer)
        right = weird.getSelectionMark(buffer)
        if left.equal(right):
          insert = left
          line = weird.getLine(buffer, insert)
          boundaries = weird.getLineBoundaries(line)

          left = weird.nextMark(insert, boundaries)
          right = weird.previousMark(insert, boundaries)

        search, flags = buffer.get_text(left, right), 0

    window.set_data("SearchFold", {'search': search})

    start = buffer.get_start_iter()
    start.set_line_offset(0)
    while start:
      hit = start.forward_search(search, 0)
      if hit:
        hit[0].set_line_offset(0)
        hit[1].forward_line()
        stop = hit[0]
        next = hit[1]
      else:
        stop = buffer.get_end_iter()
        next = None

      buffer.apply_tag(weird.fold(buffer), start, stop)
      start = next

    view.scroll_to_cursor()

  def Aunfold(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    buffer.remove_tag(weird.fold(buffer), buffer.get_start_iter(), buffer.get_end_iter())
    buffer.tag_table.remove(weird.fold(buffer))
    view.scroll_to_cursor()
    window.set_data("SearchFold", {'search': '' })
    

  def Amove_to_next_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    insert = weird.getInsertMark(buffer)
    line = weird.getLine(buffer, insert)
    boundaries = weird.getLineBoundaries(line)
    insert = weird.nextMark(insert, boundaries)
                     
    buffer.place_cursor(insert)
  
  def Amove_to_previous_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    insert = weird.getInsertMark(buffer)
    line = weird.getLine(buffer, insert)
    boundaries = weird.getLineBoundaries(line)
    insert = weird.previousMark(insert, boundaries)
        
    buffer.place_cursor(insert)  

  def Aselect_to_next_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    insert = weird.getInsertMark(buffer)
    line = weird.getLine(buffer, insert)
    boundaries = weird.getLineBoundaries(line)
    insert = weird.nextMark(insert, boundaries)
                     
    buffer.move_mark(buffer.get_insert(), insert)   
  
  def Aselect_to_previous_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    
    insert = weird.getInsertMark(buffer)
    line = weird.getLine(buffer, insert)
    boundaries = weird.getLineBoundaries(line)
    insert = weird.previousMark(insert, boundaries)
        
    buffer.move_mark(buffer.get_insert(), insert)

  def Adelete_to_next_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    buffer.begin_user_action()
    
    insert = weird.getInsertMark(buffer)
    line = weird.getLine(buffer, insert)
    boundaries = weird.getLineBoundaries(line)
    end = weird.nextMark(insert, boundaries)
                     
    buffer.delete(insert, end)   
    buffer.end_user_action()   
  
  def Adelete_to_previous_word(self, action, window):
    view = window.get_active_view()
    buffer = view.get_buffer()
    buffer.begin_user_action()
    
    insert = weird.getInsertMark(buffer)
    line = weird.getLine(buffer, insert)
    boundaries = weird.getLineBoundaries(line)
    end = weird.previousMark(insert, boundaries)
        
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
    window.set_data("SearchFold", {'search': '' })

  def deactivate(self, window):
    windowdata = window.get_data("ProperEditingPluginWindowDataKey")
    manager = window.get_ui_manager()
    manager.remove_ui(windowdata["ui_id"])
    manager.remove_action_group(windowdata["action_group"])

  def update_ui(self, window):
    view = window.get_active_view()
    windowdata = window.get_data("ProperEditingPluginWindowDataKey")
    windowdata["action_group"].set_sensitive(bool(view and view.get_editable()))
