# -*- coding: utf8 -*-
#  Advanced editing plugin
# 
#  Copyright (C) 2005 Marcus Lunzenauer <mlunzena@uos.de>
#   
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#   
#  This program is distributed in the hope that it will be useful,
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

adv_edit_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="EditMenu" action="Edit">
      <placeholder name="EditOps_5">
            <menuitem name="DeleteChar" action="DeleteChar"/>
            <menuitem name="DeleteCharBackwards" action="DeleteCharBackwards"/>

            <menuitem name="DeleteWord" action="DeleteWord"/>
            <menuitem name="DeleteWordBackwards" action="DeleteWordBackwards"/>

            <menuitem name="DeleteLine" action="DeleteLine"/>
            <menuitem name="DeleteLineBackwards" action="DeleteLineBackwards"/>

            <menuitem name="RemoveWhitespace" action="RemoveWhitespace"/>
            <menuitem name="ReduceWhitespace" action="ReduceWhitespace"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class AdvancedEditingPlugin(gedit.Plugin):
  def __init__(self):
    gedit.Plugin.__init__(self)


  def delete_char(self, action, window):
    view = window.get_active_view()
    view.do_delete_from_cursor(view, gtk.DELETE_CHARS, 1)
        
  def delete_char_bw(self, action, window):
    view = window.get_active_view()
    view.do_delete_from_cursor(view, gtk.DELETE_CHARS, -1)

  def delete_word(self, action, window):
    view = window.get_active_view()
    view.do_delete_from_cursor(view, gtk.DELETE_WORD_ENDS, 1)
        
  def delete_word_bw(self, action, window):
    view = window.get_active_view()
    view.do_delete_from_cursor(view, gtk.DELETE_WORD_ENDS, -1)

  def delete_line(self, action, window):
    view = window.get_active_view()
    view.do_delete_from_cursor(view, gtk.DELETE_PARAGRAPH_ENDS, 1)
        
  def delete_line_bw(self, action, window):
    view = window.get_active_view()
    view.do_move_cursor(view, gtk.MOVEMENT_PARAGRAPH_ENDS, -1, 0)
    view.do_delete_from_cursor(view, gtk.DELETE_PARAGRAPH_ENDS, 1)

  def remove_whitespace(self, action, window):
    view = window.get_active_view()
    view.do_delete_from_cursor(view, gtk.DELETE_WHITESPACE, 1)

  def reduce_whitespace(self, action, window):
    view = window.get_active_view()
    view.do_delete_from_cursor(view, gtk.DELETE_WHITESPACE, 1)
    view.do_insert_at_cursor(view, ' ')

  def activate(self, window):
    actions = [
      ('DeleteChar', None, 'Delete Char', None, "Delete Char", self.delete_char),
      ('DeleteCharBackwards', None, 'Delete Char Backwards', None, "Delete Char Backwards", self.delete_char_bw),

      ('DeleteWord', None, 'Delete Word', None, "Delete Word", self.delete_word),
      ('DeleteWordBackwards', None, 'Delete Word Backwards', None, "Delete Word Backwards", self.delete_word_bw),

      ('DeleteLine', None, 'Delete To End Of Line', None, "Delete To End Of Line", self.delete_line),
      ('DeleteLineBackwards', None, 'Kill Line', None, "Kill Line", self.delete_line_bw),

      ('RemoveWhitespace', None, 'Remove Whitespace', None, "Remove Whitespace", self.remove_whitespace),
      ('ReduceWhitespace', None, 'Reduce Whitespace', None, "Reduce Whitespace", self.reduce_whitespace)
    ]

    # store per window data in the window object
    windowdata = dict()
    window.set_data("AdvancedEditingPluginWindowDataKey", windowdata)

    windowdata["action_group"] = gtk.ActionGroup("GeditAdvancedEditingPluginActions")
    windowdata["action_group"].add_actions(actions, window)

    manager = window.get_ui_manager()
    manager.insert_action_group(windowdata["action_group"], -1)

    windowdata["ui_id"] = manager.add_ui_from_string(adv_edit_str)
    
    window.set_data("AdvancedEditingPluginInfo", windowdata)

  def deactivate(self, window):
    windowdata = window.get_data("AdvancedEditingPluginWindowDataKey")
    manager = window.get_ui_manager()
    manager.remove_ui(windowdata["ui_id"])
    manager.remove_action_group(windowdata["action_group"])

  def update_ui(self, window):
    view = window.get_active_view()
    windowdata = window.get_data("AdvancedEditingPluginWindowDataKey")
    windowdata["action_group"].set_sensitive(bool(view and view.get_editable()))
