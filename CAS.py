# Current state:
    # FIXME, (difficult) accidently adding ; to the end of comments instead of the end of the line
    # TODO, add a way to compile all .cas files in a folder
    # TODO, add a block comment feature
    # TODO, clean up the Scope properties 
    # TODO, change how Line.attributes works (make it a list of string and dicts rather than a dict)
    # TODO, implement the pre-pre-processor commands 
    # TODO, add enum and similar less-common stuff to the identifier 

import regex as re
import sys




# Classes 
if True:
    class Line:
        # summary:
            # Rather than having actual string-lines 
            # a Line class is made for some extra features
            # this allows attributes to be given to a line
            # and allows string-lines to be secretly added
            # both before and after the line-object
            # which is useful for parsing
        
        def __init__(self, string_):
            # find the indentation of a line, keep it seperate from the content
            self.indent  = re.sub(r'^([ \t]*).+','\g<1>',string_)
            # FIXME, this replace tabs with 4 spaces. Something more universal is needed 
            self.indent  = re.sub(r'^\t','    ',self.indent)
            
            # get the string content seperate from indentation
            self.content = re.sub(r'^[ \t]+','',string_)
            # remove trailing whitespace
            self.content = re.sub(r'[ \t]+$','',self.content)
            
            # TODO, add an original_line_number attribute
            
            # make some other properties that will be used later
            self.lines_before = []
            self.lines_after  = []
            self.attributes = dict() 
        
        def startsWith(self, string):
            # summary:
                # a method for checking to see if a 
                # line begins with a string
                
            if len(self.content) < len(string):
                return False 
            if self.content[0:len(string)] == string:
                return True
            else:
                False
        
        def startsWithPattern(self, regex_pattern):
            # summary:
                # a method for checking to see if a 
                # line begins with a regex pattern 
            return re.match(regex_pattern, self.content) != None

        def endsWith(self, string):
            # summary:
                # a method for checking to see if a 
                # line ends with a string
            if len(self.content) < len(string):
                return False 
            if self.content[-len(string):len(self.content)] == string:
                return True
            else:
                False

        def string(self):
            # summary:
                # puts together all the peices of a Line
                # then returns the output 
            return "\n".join(self.lines_before) + "\n" + self.indent + self.content + "\n".join(self.lines_after)
        
        def addLinesBefore(self, string_of_lines):
            # summary:
                # this does NOT insert the string_of_lines
                # infront of self.content 
                # instead it adds the lines to the 
                # self.lines_before list to keep 
                # the content organized for parsing
                #
                # it also automatically indents the 
                # lines that were added
            
            # turn the string into a list 
            new_lines = string_of_lines.splitlines()
            # add the indentation to all of them
            string_of_lines = ''
            for each in new_lines:
                string_of_lines += self.indent + each + '\n'
            # turn them back into a list
            new_lines = string_of_lines.splitlines()
            # insert them in the front of self.lines_before
            self.lines_before = new_lines + self.lines_before
        
        def addLinesAfter(self, string_of_lines):
            # summary:
                # this does NOT attach the string_of_lines
                # to the end of self.content 
                # instead it adds the lines to the 
                # self.lines_after list to keep 
                # the content organized for parsing
                # 
                # because of that^ each line in the string_of_lines 
                # needs to already have {}'s and ;'s for C/C++ 
                #
                # it also automatically indents the 
                # lines that were added
                
            # turn the string into a list 
            new_lines = string_of_lines.splitlines()
            # add the indentation to all of them
            string_of_lines = ''
            for each in new_lines:
                string_of_lines += self.indent + each + '\n'
            # turn them back into a list
            new_lines = string_of_lines.splitlines()
            # insert them in the front of self.lines_before
            self.lines_after = self.lines_after + new_lines
        
        def addRawLinesAfter(self, string_of_lines):
            # summary:
                # This is nearly identical to addLinesAfter
                # the only difference being, this function
                # does not automatically indent the lines
            
            # turn the string into a list 
            new_lines = string_of_lines.splitlines()
            # insert them in the front of self.lines_before
            self.lines_after = self.lines_after + new_lines
        
        def isOnlyWhitespaceOrComment(self):
            # summary:
                # returns true if the line.content only contains whitespace
                # or if the line.content only contains a comment 
            
            # check if only whitespace
            if self.content == '':
                return True
            if re.match(r'\s+$',self.content) != None:
                return True 
            # check for comment 
            if self.startsWith('//'):
                return True
            
            return False


    class Scope:
        # summary:
            # this is a one-off class (one global object)
            # it will keep track of what scopes the current 
            # line is in
            # use this to: 
                # know what scope is active
                # add lines before the start of the most recent scope
                # add lines after the most recent scope
        
        def __init__(self):
            self.names = []
            self.lines = []
        
        def addScope(self,this_name,line_):
            self.names.append(this_name)
            self.lines.append(line_)
            line_.attributes['ScopeName'] = this_name
        
        def removeScope(self):
            self.names.pop()
            self.lines.pop()
        
        def lastScope(self):
            return self.lines[-1]
        
        def add__LinesBeforeLast__Scope(self,lines_,scope_name,**kwargs):
            # summary:
                # scope_name should be either a string or None
                    # if None, then the scope_name will be ignored
                # kwargs can be 'must_have', 'rule_out_attributes', 'rule_in_attributes'
                    # each of the kwargs should be a list, a list containing only strings and dicts
                    # strings (in the list) will be checked agaisnt keys in the line's attributes
                    # dicts (in the list) will check each of its key-value pair agaisnt 
                    # the line's attribute's key-value pairs
                # examples:
                    # scope_name = "for" , rule_in_attributes = [ 'RangeBased' ]
                        # this means it will find the most recent for loop that is range based
                        # ranged based being: for( auto each : an_interable ) instead of: for (int i; i < thing; i++)
                        # it will ignore scopes not named 'for' even if (for some reason) they had a 'RangeBased' attribute
                    # scope_name = None , rule_in_attributes = [ 'conditional' ]
                        # this means it will find the most recent conditional regardless of anything else
                    
            
            # get must_have attributes
            if 'must_have' in kwargs: must_have = kwargs['must_have']
            else: must_have = []
            # get rule_out_attributes
            if 'rule_out_attributes' in kwargs: rule_in_attributes = kwargs['rule_out_attributes']
            else: rule_out_attributes = []
            # get rule_in_attributes
            if 'rule_in_attributes' in kwargs: rule_in_attributes = kwargs['rule_in_attributes']
            else: rule_in_attributes = []


            # the loop needs to go backwards because 
            # the most recent (Last) Scope is going to 
            # be at the end of the list
            each_line_index = len(self.names)
            for dont_use_this in range(0,len(self.lines)):
                # decrement each_line_index by 1 
                each_line_index -= 1
                skip_line = False
                # if the name matches, or no scope_name
                # then check the attributes
                if self.names[each_line_index] == scope_name or scope_name == None:
                    # check must_have attributes
                    for each_attribute in must_have:
                        # if the element is a dict, then all keys and values 
                        # must be in the line's attributes
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if missing any key, then skip 
                                if each_key not in self.lines[each_line_index].attributes:
                                    skip_line = True
                                    break
                                # if key's value is different, then skip
                                elif self.lines[each_line_index].attributes[each_key] != each_attribute[each_key]:
                                    skip_line = True
                                    break
                        
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            if skip_line == True:
                                break
                        
                        # if the element is a string, 
                        # then that element needs to be a key-name
                        # for something in the line's attributes
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line is missing a single key, then skip it
                            if each_attribute not in self.lines[each_line_index].attributes:
                                skip_line = True
                                break
                        
                        if skip_line == True:
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            break
                            
                    if skip_line == True:
                        # this is here because of nested for loops 
                        # if skip_line is True, then it means 
                        # a nested for loop wanted to continue on 'for each_line'
                        # (when depth = 0, then 'continue' is used instead of 'break')
                        # nested_depth = 0 
                        continue
                        
                    # check rule_out_attributes
                    for each_attribute in rule_out_attributes:
                            # if the element is a dict, then both key and value must
                            # must be in the line's attributes 
                            # before the line can be ruled out
                            if type(each_attribute) == dict:
                                for each_key in each_attribute:
                                    # if has key, then check value
                                    if each_key in self.lines[each_line_index].attributes:
                                        # if value matches, then skip_line 
                                        if self.lines[each_line_index].attributes[each_key] == each_attribute[each_key]:
                                            skip_line = True
                                            break

                                if skip_line == True:
                                    # this is here because of nested for loops 
                                    # if skip_line is True, then it means 
                                    # a nested for loop wanted to continue on 'for each_line'
                                    # (when depth = 0, then 'continue' is used instead of 'break')
                                    # nested_depth = 1
                                    break
                            
                            # if the element is a string, 
                            # then if the line's attributes has that string as 
                            # a key, then it will be ruled out
                            # (however the key's value does not matter)
                            elif type(each_attribute) == str:
                                # if the line has a single key, then skip it
                                if each_attribute in self.lines[each_line_index].attributes:
                                    skip_line = True
                                    break
                            
                            if skip_line == True:
                                # this is here because of nested for loops 
                                # if skip_line is True, then it means 
                                # a nested for loop wanted to continue on 'for each_line'
                                # (when depth = 0, then 'continue' is used instead of 'break')
                                # nested_depth = 1
                                break
                                
                    if skip_line == True:
                        # this is here because of nested for loops 
                        # if skip_line is True, then it means 
                        # a nested for loop wanted to continue on 'for each_line'
                        # (when depth = 0, then 'continue' is used instead of 'break')
                        # nested_depth = 0 
                        continue
                        
                    # check rule_in_attributes
                    for each_attribute in rule_in_attributes:
                        # if the element is a dict, then both key and value must
                        # be in the line's attributes before the line can 
                        # be ruled in
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if has key, then check value
                                if each_key in self.lines[each_line_index].attributes:
                                    # if value matches, then process line, and end method (return)
                                    if self.lines[each_line_index].attributes[each_key] == each_attribute[each_key]:
                                        self.lines[each_line_index].addLinesBefore(lines_)
                                        return
                        
                        # if the element is a string, 
                        # then if the line's attributes has that string as 
                        # a key, then it will be ruled in
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line has a single key, then skip it
                            if each_attribute in self.lines[each_line_index].attributes:
                                self.lines[each_line_index].addLinesBefore(lines_)
                                return

        def add__LinesAfterLast__Scope(self,lines_,scope_name,**kwargs):
            # summary:
                # scope_name should be either a string or None
                    # if None, then the scope_name will be ignored
                # kwargs can be 'must_have', 'rule_out_attributes', 'rule_in_attributes'
                    # each of the kwargs should be a list, a list containing only strings and dicts
                    # strings (in the list) will be checked agaisnt keys in the line's attributes
                    # dicts (in the list) will check each of its key-value pair agaisnt 
                    # the line's attribute's key-value pairs
                # examples:
                    # scope_name = "for" , rule_in_attributes = [ 'RangeBased' ]
                        # this means it will find the most recent for loop that is range based
                        # ranged based being: for( auto each : an_interable ) instead of: for (int i; i < thing; i++)
                        # it will ignore scopes not named 'for' even if (for some reason) they had a 'RangeBased' attribute
                    # scope_name = None , rule_in_attributes = [ 'conditional' ]
                        # this means it will find the most recent conditional regardless of anything else
                    
            
            # get must_have attributes
            if 'must_have' in kwargs: must_have = kwargs['must_have']
            else: must_have = []
            # get rule_out_attributes
            if 'rule_out_attributes' in kwargs: rule_in_attributes = kwargs['rule_out_attributes']
            else: rule_out_attributes = []
            # get rule_in_attributes
            if 'rule_in_attributes' in kwargs: rule_in_attributes = kwargs['rule_in_attributes']
            else: rule_in_attributes = []


            # the loop needs to go backwards because 
            # the most recent (Last) Scope is going to 
            # be at the end of the list
            each_line_index = len(self.names)
            for dont_use_this in range(0,len(self.lines)):
                # decrement each_line_index by 1 
                each_line_index -= 1
                skip_line = False
                # if the name matches, or no scope_name
                # then check the attributes
                if self.names[each_line_index] == scope_name or scope_name == None:
                    # check must_have attributes
                    for each_attribute in must_have:
                        # if the element is a dict, then all keys and values 
                        # must be in the line's attributes
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if missing any key, then skip 
                                if each_key not in self.lines[each_line_index].attributes:
                                    skip_line = True
                                    break
                                # if key's value is different, then skip
                                elif self.lines[each_line_index].attributes[each_key] != each_attribute[each_key]:
                                    skip_line = True
                                    break
                        
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            if skip_line == True:
                                break
                        
                        # if the element is a string, 
                        # then that element needs to be a key-name
                        # for something in the line's attributes
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line is missing a single key, then skip it
                            if each_attribute not in self.lines[each_line_index].attributes:
                                skip_line = True
                                break
                        
                        if skip_line == True:
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            break
                            
                    if skip_line == True:
                        # this is here because of nested for loops 
                        # if skip_line is True, then it means 
                        # a nested for loop wanted to continue on 'for each_line'
                        # (when depth = 0, then 'continue' is used instead of 'break')
                        # nested_depth = 0 
                        continue
                        
                    # check rule_out_attributes
                    for each_attribute in rule_out_attributes:
                            # if the element is a dict, then both key and value must
                            # must be in the line's attributes 
                            # before the line can be ruled out
                            if type(each_attribute) == dict:
                                for each_key in each_attribute:
                                    # if has key, then check value
                                    if each_key in self.lines[each_line_index].attributes:
                                        # if value matches, then skip_line 
                                        if self.lines[each_line_index].attributes[each_key] == each_attribute[each_key]:
                                            skip_line = True
                                            break

                                if skip_line == True:
                                    # this is here because of nested for loops 
                                    # if skip_line is True, then it means 
                                    # a nested for loop wanted to continue on 'for each_line'
                                    # (when depth = 0, then 'continue' is used instead of 'break')
                                    # nested_depth = 1
                                    break
                            
                            # if the element is a string, 
                            # then if the line's attributes has that string as 
                            # a key, then it will be ruled out
                            # (however the key's value does not matter)
                            elif type(each_attribute) == str:
                                # if the line has a single key, then skip it
                                if each_attribute in self.lines[each_line_index].attributes:
                                    skip_line = True
                                    break
                            
                            if skip_line == True:
                                # this is here because of nested for loops 
                                # if skip_line is True, then it means 
                                # a nested for loop wanted to continue on 'for each_line'
                                # (when depth = 0, then 'continue' is used instead of 'break')
                                # nested_depth = 1
                                break
                                
                    if skip_line == True:
                        # this is here because of nested for loops 
                        # if skip_line is True, then it means 
                        # a nested for loop wanted to continue on 'for each_line'
                        # (when depth = 0, then 'continue' is used instead of 'break')
                        # nested_depth = 0 
                        continue
                        
                    # check rule_in_attributes
                    for each_attribute in rule_in_attributes:
                        # if the element is a dict, then both key and value must
                        # be in the line's attributes before the line can 
                        # be ruled in
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if has key, then check value
                                if each_key in self.lines[each_line_index].attributes:
                                    # if value matches, then process line, and end method (return)
                                    if self.lines[each_line_index].attributes[each_key] == each_attribute[each_key]:
                                        self.lines[each_line_index].addLinesAfter(lines_)
                                        return
                        
                        # if the element is a string, 
                        # then if the line's attributes has that string as 
                        # a key, then it will be ruled in
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line has a single key, then skip it
                            if each_attribute in self.lines[each_line_index].attributes:
                                self.lines[each_line_index].addLinesAfter(lines_)
                                return

        def add__LinesAfterFirst__Scope(self,lines_,scope_name):
            # summary:
                # scope_name should be either a string or None
                    # if None, then the scope_name will be ignored
                # kwargs can be 'must_have', 'rule_out_attributes', 'rule_in_attributes'
                    # each of the kwargs should be a list, a list containing only strings and dicts
                    # strings (in the list) will be checked agaisnt keys in the line's attributes
                    # dicts (in the list) will check each of its key-value pair agaisnt 
                    # the line's attribute's key-value pairs
                # examples:
                    # scope_name = "for" , rule_in_attributes = [ 'RangeBased' ]
                        # this means it will find the first (largest parent) for loop that is range based
                        # ranged based being: for( auto each : an_interable ) instead of: for (int i; i < thing; i++)
                        # it will ignore scopes not named 'for' even if (for some reason) they had a 'RangeBased' attribute
                    # scope_name = None , rule_in_attributes = [ 'conditional' ]
                        # this means it will find the first (largest parent) conditional regardless of anything else
                    
            
            # get must_have attributes
            if 'must_have' in kwargs: must_have = kwargs['must_have']
            else: must_have = []
            # get rule_out_attributes
            if 'rule_out_attributes' in kwargs: rule_in_attributes = kwargs['rule_out_attributes']
            else: rule_out_attributes = []
            # get rule_in_attributes
            if 'rule_in_attributes' in kwargs: rule_in_attributes = kwargs['rule_in_attributes']
            else: rule_in_attributes = []


            for each_line_index in range(0,len(self.lines)): 
                skip_line = False
                # if the name matches, or no scope_name
                # then check the attributes
                if self.names[each_line_index] == scope_name or scope_name == None:
                    # check must_have attributes
                    for each_attribute in must_have:
                        # if the element is a dict, then all keys and values 
                        # must be in the line's attributes
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if missing any key, then skip 
                                if each_key not in self.lines[each_line_index].attributes:
                                    skip_line = True
                                    break
                                # if key's value is different, then skip
                                elif self.lines[each_line_index].attributes[each_key] != each_attribute[each_key]:
                                    skip_line = True
                                    break
                        
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            if skip_line == True:
                                break
                        
                        # if the element is a string, 
                        # then that element needs to be a key-name
                        # for something in the line's attributes
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line is missing a single key, then skip it
                            if each_attribute not in self.lines[each_line_index].attributes:
                                skip_line = True
                                break
                        
                        if skip_line == True:
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            break
                            
                    if skip_line == True:
                        # this is here because of nested for loops 
                        # if skip_line is True, then it means 
                        # a nested for loop wanted to continue on 'for each_line'
                        # (when depth = 0, then 'continue' is used instead of 'break')
                        # nested_depth = 0 
                        continue
                      
                    # check rule_out_attributes
                    for each_attribute in rule_out_attributes:
                        # if the element is a dict, then both key and value must
                        # must be in the line's attributes 
                        # before the line can be ruled out
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if has key, then check value
                                if each_key in self.lines[each_line_index].attributes:
                                    # if value matches, then skip_line 
                                    if self.lines[each_line_index].attributes[each_key] == each_attribute[each_key]:
                                        skip_line = True
                                        break

                            if skip_line == True:
                                # this is here because of nested for loops 
                                # if skip_line is True, then it means 
                                # a nested for loop wanted to continue on 'for each_line'
                                # (when depth = 0, then 'continue' is used instead of 'break')
                                # nested_depth = 1
                                break
                        
                        # if the element is a string, 
                        # then if the line's attributes has that string as 
                        # a key, then it will be ruled out
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line has a single key, then skip it
                            if each_attribute in self.lines[each_line_index].attributes:
                                skip_line = True
                                break
                        
                        if skip_line == True:
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            break
                            
                    if skip_line == True:
                        # this is here because of nested for loops 
                        # if skip_line is True, then it means 
                        # a nested for loop wanted to continue on 'for each_line'
                        # (when depth = 0, then 'continue' is used instead of 'break')
                        # nested_depth = 0 
                        continue
                      
                    # check rule_in_attributes
                    for each_attribute in rule_in_attributes:
                        # if the element is a dict, then both key and value must
                        # be in the line's attributes before the line can 
                        # be ruled in
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if has key, then check value
                                if each_key in self.lines[each_line_index].attributes:
                                    # if value matches, then process line, and end method (return)
                                    if self.lines[each_line_index].attributes[each_key] == each_attribute[each_key]:
                                        self.lines[each_line_index].addLinesAfter(lines_)
                                        return
                        
                        # if the element is a string, 
                        # then if the line's attributes has that string as 
                        # a key, then it will be ruled in
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line has a single key, then skip it
                            if each_attribute in self.lines[each_line_index].attributes:
                                self.lines[each_line_index].addLinesAfter(lines_)
                                return

        def add__LinesBeforeFirst__Scope(self,lines_,scope_name):
            # summary:
                # scope_name should be either a string or None
                    # if None, then the scope_name will be ignored
                # kwargs can be 'must_have', 'rule_out_attributes', 'rule_in_attributes'
                    # each of the kwargs should be a list, a list containing only strings and dicts
                    # strings (in the list) will be checked agaisnt keys in the line's attributes
                    # dicts (in the list) will check each of its key-value pair agaisnt 
                    # the line's attribute's key-value pairs
                # examples:
                    # scope_name = "for" , rule_in_attributes = [ 'RangeBased' ]
                        # this means it will find the first (largest parent) for loop that is range based
                        # ranged based being: for( auto each : an_interable ) instead of: for (int i; i < thing; i++)
                        # it will ignore scopes not named 'for' even if (for some reason) they had a 'RangeBased' attribute
                    # scope_name = None , rule_in_attributes = [ 'conditional' ]
                        # this means it will find the first (largest parent) conditional regardless of anything else
                    
            
            # get must_have attributes
            if 'must_have' in kwargs: must_have = kwargs['must_have']
            else: must_have = []
            # get rule_out_attributes
            if 'rule_out_attributes' in kwargs: rule_in_attributes = kwargs['rule_out_attributes']
            else: rule_out_attributes = []
            # get rule_in_attributes
            if 'rule_in_attributes' in kwargs: rule_in_attributes = kwargs['rule_in_attributes']
            else: rule_in_attributes = []


            for each_line_index in range(0,len(self.lines)): 
                skip_line = False
                # if the name matches, or no scope_name
                # then check the attributes
                if self.names[each_line_index] == scope_name or scope_name == None:
                    # check must_have attributes
                    for each_attribute in must_have:
                        # if the element is a dict, then all keys and values 
                        # must be in the line's attributes
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if missing any key, then skip 
                                if each_key not in self.lines[each_line_index].attributes:
                                    skip_line = True
                                    break
                                # if key's value is different, then skip
                                elif self.lines[each_line_index].attributes[each_key] != each_attribute[each_key]:
                                    skip_line = True
                                    break
                        
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            if skip_line == True:
                                break
                        
                        # if the element is a string, 
                        # then that element needs to be a key-name
                        # for something in the line's attributes
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line is missing a single key, then skip it
                            if each_attribute not in self.lines[each_line_index].attributes:
                                skip_line = True
                                break
                        
                        if skip_line == True:
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            break
                            
                    if skip_line == True:
                        # this is here because of nested for loops 
                        # if skip_line is True, then it means 
                        # a nested for loop wanted to continue on 'for each_line'
                        # (when depth = 0, then 'continue' is used instead of 'break')
                        # nested_depth = 0 
                        continue
                      
                    # check rule_out_attributes
                    for each_attribute in rule_out_attributes:
                        # if the element is a dict, then both key and value must
                        # must be in the line's attributes 
                        # before the line can be ruled out
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if has key, then check value
                                if each_key in self.lines[each_line_index].attributes:
                                    # if value matches, then skip_line 
                                    if self.lines[each_line_index].attributes[each_key] == each_attribute[each_key]:
                                        skip_line = True
                                        break

                            if skip_line == True:
                                # this is here because of nested for loops 
                                # if skip_line is True, then it means 
                                # a nested for loop wanted to continue on 'for each_line'
                                # (when depth = 0, then 'continue' is used instead of 'break')
                                # nested_depth = 1
                                break
                        
                        # if the element is a string, 
                        # then if the line's attributes has that string as 
                        # a key, then it will be ruled out
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line has a single key, then skip it
                            if each_attribute in self.lines[each_line_index].attributes:
                                skip_line = True
                                break
                        
                        if skip_line == True:
                            # this is here because of nested for loops 
                            # if skip_line is True, then it means 
                            # a nested for loop wanted to continue on 'for each_line'
                            # (when nested_depth = 0, then 'continue' is used instead of 'break')
                            # nested_depth = 1
                            break
                            
                    if skip_line == True:
                        # this is here because of nested for loops 
                        # if skip_line is True, then it means 
                        # a nested for loop wanted to continue on 'for each_line'
                        # (when depth = 0, then 'continue' is used instead of 'break')
                        # nested_depth = 0 
                        continue
                      
                    # check rule_in_attributes
                    for each_attribute in rule_in_attributes:
                        # if the element is a dict, then both key and value must
                        # be in the line's attributes before the line can 
                        # be ruled in
                        if type(each_attribute) == dict:
                            for each_key in each_attribute:
                                # if has key, then check value
                                if each_key in self.lines[each_line_index].attributes:
                                    # if value matches, then process line, and end method (return)
                                    if self.lines[each_line_index].attributes[each_key] == each_attribute[each_key]:
                                        self.lines[each_line_index].addLinesBefore(lines_)
                                        return
                        
                        # if the element is a string, 
                        # then if the line's attributes has that string as 
                        # a key, then it will be ruled in
                        # (however the key's value does not matter)
                        elif type(each_attribute) == str:
                            # if the line has a single key, then skip it
                            if each_attribute in self.lines[each_line_index].attributes:
                                self.lines[each_line_index].addLinesBefore(lines_)
                                return
    
    CURRENT_SCOPES = Scope()

    # FIXME, this is part of a future feature
    # it will be a part of pre-pre-processor commands
        #class InsertTag:
        #    def __init__(self):
        #        self.lines_ = []
        #    def output(self):
        #        return '\n'.join(self.lines)



# built_in_commands 
if True:
    # summary:
        # for now built_in_commands are the only commands
        # however in the future there will probably be custom commands
    
    def SemicolonChecker(TheLine,TheNextNonWhitespaceLine):
        # summary:
            # this is the function that handles adding all of the ; as delimiters 

        # lines starting with # dont put ;
        if TheLine.startsWith('#'):
            return    
        # lines that are all-whitespace dont put ;
        elif TheLine.isOnlyWhitespaceOrComment():
            return
        # if there is no next line, then just add the ';'
        if TheNextNonWhitespaceLine == None:
            TheLine.content += ';'
        # if next non-whitespace line is more indented, dont put ;
        elif len(TheNextNonWhitespaceLine.indent) > len(TheLine.indent):
            return
        # if its a template, then dont put ;
        elif TheLine.startsWithPattern('template *'):
            return
        # else put a semicolon at the end of it!
        else:
            TheLine.content += ';'

    def BracketsAdder(TheLine, TheNextNonWhitespaceLine):
        # summary:
            # this is the function that handles adding all the {}'s
            # to each place they need to go
        
        # skip only-whitespace/comment lines 
        if TheLine.isOnlyWhitespaceOrComment():
            return

        # if there is no next-line, then close all the currently-left-open brackets
        if TheNextNonWhitespaceLine == None:
            add_to_end = ''
            for each in range(0,len(CURRENT_SCOPES.lines)):
                # add a bracket / comment
                add_to_end += '\n' + CURRENT_SCOPES.lastScope().indent + CURRENT_SCOPES.lastScope().attributes['PutAfterBlockEnd'] 
                # remove them from the scope
                CURRENT_SCOPES.removeScope()
            lines_[-2].addRawLinesAfter(add_to_end)
            return
        
        # if next non-whitespace line is less indented,
        # the add the right number of '}'s 
        if len(TheNextNonWhitespaceLine.indent) < len(TheLine.indent):
            # 'this_indent' is the indent that is ending the current block
            # for example:
                    #if 5 > 3
                    #    print '5 > 3'
                    #else
                # the indent of the 'else' line would be the 'this_indent' because it's ending the if block
            this_indent = len(TheNextNonWhitespaceLine.indent)
            
            # check that the un-indent is inline with one of the scopes 
            each_index = 0
            while True:
                # decrement because the values are going to be 
                # cycled through backwards
                # e.g. list[-1], list[-2], list[-3], etc
                each_index -= 1
                # break if greater than the -length
                if -each_index > len(CURRENT_SCOPES.lines):
                    break
                # 'scope_indent' is the indent of one of the larger scopes
                # for example:
                        #if 5 > 3
                        #    print '5 > 3'
                    # the indent of the 'if' line would be the 'scope_indent' 
                    # because it's the line before start of the most recent scope
                scope_indent = len( CURRENT_SCOPES.lines[each_index].indent )
                # if the length matches then thats the number of scopes that need to be closed
                if scope_indent == this_indent:
                    add_to_end = ''
                    for each in range(0,-each_index):
                        # FIXME, classes and structs need ;'s after their }
                        # add a bracket and/or comment
                        if 'PutAfterBlockEnd' in CURRENT_SCOPES.lastScope().attributes:
                            add_to_end += '\n' + CURRENT_SCOPES.lastScope().indent + CURRENT_SCOPES.lastScope().attributes['PutAfterBlockEnd'] 
                        # remove them from the scope
                        CURRENT_SCOPES.removeScope()
                    
                    # add the closing brackets to TheLine
                    TheLine.addRawLinesAfter(add_to_end)
                    
                
                # when the indent is larger than the scope indent 
                # then there's a problem 
                # for example:
                        #if 3 > 5:
                        #    print "3 > 5"
                        #  else 
                    # the 'else' isn't inline with the 'print' but its not 
                    # inline with the 'if' either
                # if the next line is smaller, then we need to go out a scope (keep looping)
                elif this_indent < scope_indent:
                    continue
                    
                elif this_indent > scope_indent:
                    # make sure a bigger scope exists
                    #if len(CURRENT_SCOPES.lines) > each_index:
                        # check to make sure its bigger than the next scope
                    # FIXME, improve this error/warning message 
                    print "Hey, there's a line and I don't think it is indented correctly\nits: " + TheNextNonWhitespaceLine.content
                    exit(1)
                    
                # the code should never get here since 
                # this_indent should either be >, <, or == scope_indent
                else:
                    print "You should not have been able to get here haha\nsee why by searching the code for 209348590425842"
                
        # if next non-whitespace line is more indented,
        # add a scope, add a {
        if len(TheNextNonWhitespaceLine.indent) > len(TheLine.indent):
            
            # by default 
            if TheLine.endsWith(';'):
                TheLine.attributes['PutAfterBlockEnd'] = '};'
                # remove the ';'
                TheLine.content = TheLine.content[0:-1]
            else:
                TheLine.attributes['PutAfterBlockEnd'] = '}'
            
            # dont forget to add the { 
            TheLine.attributes['PutBeforeBlockStart'] = ' {'
            
            
            # this decides the type of scope
            # this will mostly be used later as part of the 
            # pre-pre-processor features 
            if TheLine.startsWithPattern(r'if(\s|\()'):
                # add ()'s to the conditional
                TheLine.content = re.sub(r'^if ((?:.|\n)+)','if (\g<1>)', TheLine.content)
                # add attributes
                TheLine.attributes['conditional'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('if',TheLine)
                
            elif TheLine.startsWithPattern(r'else(\s|)$'):
                # add attributes
                TheLine.attributes['conditional'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('else',TheLine)
                
            elif TheLine.startsWithPattern(r'else *if(\s|\()'):
                # add attributes
                TheLine.attributes['conditional'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('else if',TheLine)
                
            # check switch/case
            elif TheLine.startsWithPattern(r'switch[ \(]'):
                # add ()'s to the conditional
                TheLine.content = re.sub(r'^switch ((?:.|\n)+)','switch (\g<1>)',TheLine.content)
                # add attributes
                TheLine.attributes['conditional'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('switch',TheLine)
            
            elif TheLine.startsWithPattern(r'case(\s|\()'):
                # add attributes
                TheLine.attributes['conditional'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('case',TheLine)
            
            # check while 
            elif TheLine.startsWithPattern(r'while(\s|\()'):
                # add ()'s to the conditional
                TheLine.content = re.sub(r'^while ((?:.|\n)+)','while (\g<1>)', TheLine.content)
                # add attributes
                TheLine.attributes['conditional'] = True
                TheLine.attributes['loop'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('while',TheLine)
                
            # check for 
            elif TheLine.startsWithPattern(r'for(\s|\()'):
                # add ()'s to the conditional
                TheLine.content = re.sub(r'^for ((?:.|\n)+)','for (\g<1>)', TheLine.content)
                # add attributes
                TheLine.attributes['conditional'] = True
                TheLine.attributes['loop'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('for',TheLine)
            
            # check main
            elif TheLine.startsWithPattern(r'int *main *\('):
                # add attributes
                TheLine.attributes['main'] = True
                TheLine.attributes['PutAfterBlockEnd'] += '// end main'
                # enter the scope
                CURRENT_SCOPES.addScope('main',TheLine)
            
            # check class 
            elif TheLine.startsWith(r'class '):
                # add attributes
                TheLine.attributes['class'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('class',TheLine)
            
            # check struct
            elif TheLine.startsWith(r'struct '):
                # add attributes
                TheLine.attributes['struct'] = True
                # enter the scope
                CURRENT_SCOPES.addScope('struct',TheLine)
            
            # check function
            # FIXME, change the pattern to not accept impossible types and to not overlap with class/struct
            # FIXME, this will fail with templating and ::'s and .'s fix it!
            elif TheLine.startsWithPattern(r'[\w\d_]+( +[\w\d_]+)+\((?:.|\n)+\)'):
                # add attributes
                TheLine.attributes['function'] = True
                # FIXME, add the function's name using regex or something 
                # enter the scope
                CURRENT_SCOPES.addScope('function',TheLine)
                
            # check blank scope
            else:
                CURRENT_SCOPES.addScope('unknown',TheLine)


            # add things to the start
            TheLine.content = TheLine.content + TheLine.attributes['PutBeforeBlockStart']

            # end process
            return

    # add the functions to the built_in_commands list 
    built_in_commands = []
    built_in_commands.append(SemicolonChecker)
    built_in_commands.append(BracketsAdder)


# FIXME, pre-pre-processor future-features
    # before_parse_commands = []
    # CAS_phrases     = ['//:', '//:Before', '//:After', '//:BeforeParse']
    # before_commands = []
    # after_commands  = []


# Phase 0 
if True:
    # summary:
        # get the arguments from when this function is called
        # get the filename from the arguments
        # figure out if the user wants to print/compile/run the .cas file
        # by default the g++ command is used to compile C++
    
    # get the first argument 
    arg1 = str(sys.argv[1])
    
    print_output_file = False 
    compile_code      = False
    run_code          = False
    name_of_output_file = 'a.cpp'
    make_output_code_file = True
    
    if arg1 == 'run':
        run_code = True
        compile_code = True
        make_output_code_file = True
        filename = str(sys.argv[2])
    elif arg1 == 'compile':
        compile_code = True
        make_output_code_file = True
        filename = str(sys.argv[2])
    elif arg1 == 'print':
        print_output_file = True
        make_output_code_file = False
        filename = str(sys.argv[2])
    else:
        filename = str(sys.argv[1])
    
    if len(sys.argv) == 4:
        name_of_output_file = str(sys.argv[3])
        
    the_file       = open(filename,'r+')
    lines_         = the_file.read()
    the_file.close()


# Phase 1
if True:
    # summary:
        # this phase gets the text and turns it into a list of strings
        # it then turns those strings into Line objects
            # (Line objects can actually contain newline characters)
            # (this is because one line of code can span multiple editor-lines)
            # (Each 'line' of code meaning code that needs a semicolon at the end)
        # while it's doing that, it checks for lines that end with \
            # if there is a \
            # then the next string-line is put into the same Line object
            # then the \ is removed (but the newline stays) 
            # Ex:
                # string a_string = "hello " + \
                #                            "world"
                #^ that would be 1 line object, even though its two lines
    # convert string to list of string-lines 
    lines_ = lines_.splitlines()
    line_index = -1
    # break once all lines have been checked
    while line_index + 1 < len(lines_):
        # iterate 
        line_index += 1
        
        # convert the current str-line into a Line object 
        lines_[line_index] = Line(lines_[line_index])
        
        # check for ending with a \
        # if the line is empty, then it can't end with a \
        while (len(lines_[line_index].content) >= 1):
            # if the line doesnt end with a \
            # then go to the next line (aka break)
            if lines_[line_index].content[-1] != '\\':
                break
            # if the next index doesnt exist 
            # then the \ doesnt mean anything 
            if line_index + 1 >= len(lines_):
                break
            
            # remove the \
            lines_[line_index].content = lines_[line_index].content[0:-1]
            # add the string-line to the Line object 
            lines_[line_index].content += '\n' + lines_[line_index+1]
            # remove the string-line from the list
            del lines_[line_index+1]
            # no need to iterate because the list got shorter 
            # (shorter because an element was just deleted)
        


# Phase 2, FIXME, the below commented-out code works, but 
# it is not useful till other pre-pre-processor features are developed
    ## check all lines for ## vars
    #all_tag_names = []
    #for each in lines_:
    #    if re.match(r'##([\w\d_]+)$',each.content) != None:
    #        tag_name = re.sub(r'##([\w\d_]+)','\g<1>' ,each.content)
    #        all_tag_names.add(tag_name)
    #        # create the var 
    #        exec(tag_name +' = InsertTag()')
# FIXME, future-feature
# this will be a kind of pre-pre-processor command 
    # check all lines for //:BeforeEverything blocks
    #for each in lines_:
    #    if each.startsWith('//:BeforeEverything'):
    #        # FIXME, get/find the code for finding a block



# Phase 3, start processing
if True:
    # summary:
        # this runs all of the functions 
        # that are going to be manipulating the code
        # in order to transform it into C++ code
        #
        # the functions are run in a particular order 
        # all functions are run for each line
        
    # Why None is added to lines_:
        # because the editing-functions will use/need a 'TheNextLine' var
        # there is a None element at the end to show that there is no next line 
            # otherwise instead of None, python would
            # throw an out of index error and since
            # some editor-fucntions behave differently on the 
            # last line
            # having a testable None seems like a good way 
            # to inform the function that TheNextLine doesn't exist
    lines_.append(None)
    each_line_index = -1
    end_processing_loop = False 
    while True:
        # the last element in lines_ is None
        # so when on the 2nd-to-last line remove the None and break the loop 
        if each_line_index+2 >= len(lines_):
            # remove the None element since it was only needed 
            # for this while loop
            lines_.pop()
            break
        # loop increment 
        # this is a while loop because sometimes other parts
        # of the code need to skip-ahead on the incrementor
        each_line_index += 1
        
        
        # find the next_non_whitespace_line_index
        next_non_whitespace_line_index = each_line_index
        while True:
            next_non_whitespace_line_index += 1
            
            # if that index is past the 2nd-to-last element
            # then break 
            if next_non_whitespace_line_index >= len(lines_)-1:
                break
            # if its not whitespace
            # then break
            if not lines_[next_non_whitespace_line_index].isOnlyWhitespaceOrComment():
                break

        

        # FIXME, all part of the pre-pre-processor feature 
            ##run 'BeforeParse' commands
            #for each_func in before_parse_commands:
            #    each_func(lines_[each_line_index],lines_[next_non_whitespace_line_index])
            #
            ##check for XDP_CPP commands
            #if each.content in XDP_CPP_phrases:
            #    # FIXME, do something 
            #    pass
            #
            ##run 'Before' commands
            #for each_func in before_commands:
            #    each_func(lines_[each_line_index],lines_[next_non_whitespace_line_index])
        
        #run built_in commands
        for each_func in built_in_commands:    
            each_func(lines_[each_line_index],lines_[next_non_whitespace_line_index])
            
        # FIXME, part of the pre-pre-processor feature
            ##run 'After' commands
            #for each_func in after_commands:
            #    each_func(lines_[each_line_index],lines_[next_non_whitespace_line_index])


    # join all the Line objects together 
    final_code_product = ''
    for each in lines_:
        final_code_product += each.string() 


# FIXME, part of the pre-pre-processor feature
    ##replace ## stuff
    #for each in all_tag_names:
    #    exec(r'everything = re.sub(r"(^|\n)##'+each+'",'+each+'.output(), everything)')



# Phase 4, output 
if True:
    # summary:
        # this prints, compiles, and runs the code
        # depending on what commands were given
    
    if print_output_file:
        print final_code_product

    if make_output_code_file:
        # create output 
        output_file = open( name_of_output_file,"w+")
        output_file.write(final_code_product)
        output_file.close()

    if compile_code or run_code:
        # create a cpp build file with g++
        import os
        # warning check 
        if name_of_output_file[-3:len(name_of_output_file)] != 'cpp':
            print "Hey the name of your output file doesn't include .cpp at the end"
            # TODO, add a question here that lets the user add the .cpp without re-running the command
        # FIXME, name_of_output_file will have problems with stuff that needs to be escaped
        
        # remove the file extension (which is almost allways .cpp)
        name_without_extention = re.sub(r'\.\w+$','',name_of_output_file)
        os.system('g++ "'+name_of_output_file+'" -o "'+name_without_extention+'.out"')

    if run_code:
        # run the code 
        import os
        # FIXME, name_of_output_file will have problems with stuff that needs to be escaped
        os.system('./"'+name_without_extention+'.out"')
        









