# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 14:46:48 2021

@author: Lucas
"""
import sys, datetime, urllib.request, re, os, io
FL_Folder = "C:\\Users\\Lucas\\source\\Python\\YGO\\FL_List"
Test_Output = FL_Folder + "\\Output\\output.txt"
Test_Page = "C:\\Users\\Lucas\\source\\Python\\YGO\\FL_List\\Test\\Forbidden & Limited Card List Yu-Gi-Oh! TRADING CARD GAME.htm"
Status_Enumerable = ["Forbidden", "Limited", "Semi-Limited", "Unlimited"]

def PrintTextFile(FilePath: str, FileContents: str, OverwritePrevious = False):
    
    ## Submethod to rename a duplicate file
    def Rename_Duplicate(Savepath):
        
        ## Sub-Submethod to get current working directory of the parent
        def Get_Parent_Directory(path = os.getcwd()): return path.split('\\')[:-1]
        
        duplicate_copy_counter = []
        file_array = Savepath.split('\\')[-1].split('.')
        
        if len(file_array) <= 1: 
            raise Exception(message = 'Error in \'Rename_Duplicate\'; \'Savepath\' must be splittable by \'.\'')
            
        filename_regex = re.compile(file_array[0] + '\d*')
        
        for list_file in os.listdir('\\'.join(Savepath.split('\\')[:-1])):
            if re.match(filename_regex, list_file.split('.')[0]): 
                duplicate_copy_counter.append(list_file)
                
        return '\\'.join(Get_Parent_Directory(Savepath)) + '\\' + file_array[0] + str(len(duplicate_copy_counter)) + '.' + file_array[1]
    
    ## Rename the duplicate file if we don't want to overwrite
    if(not OverwritePrevious): FilePath = Rename_Duplicate(FilePath)
    
    ## Write the file contents
    with io.open(FilePath, "w+", encoding="utf-8") as TargetFile: TargetFile.write(FileContents)
    
    return

class FL_Entry:
    Type = None
    Name = None
    Status_Advanced = None
    Status_Traditional = None
    Remarks = None
    Link = None
    
    def ToTuple(self):
        return(
            self.Type,
            self.Name,
            self.Status_Advanced,
            self.Status_Traditional,
            self.Remarks,
            self.Link
            )
    
    def ToPropertyTyples(self):
        for(index, property) in self.Properties:
            yield(self.Name, index, property)
    
    def ToString(self):
        return "Type: {cTyp}\nName: {cNam}\nAdvanced: {cAdv}\nTraditional: {cTra}\nRemarks: {cRem}\nLink: {cLnk}\n".format(
            cTyp = self.Type, 
            cNam = self.Name, 
            cAdv = self.Status_Advanced, 
            cTra = self.Status_Traditional,
            cRem = self.Remarks,
            cLnk = self.Link
            )

def GetCurrentListHTML():
    ## Get the HTML Page from the UK site and convert it from bytes to text
    PageHTML = ""
    with urllib.request.urlopen("https://img.yugioh-card.com/uk/gameplay/detail.php?id=1155") as URLReader:
        PageHTML = URLReader.read().decode("utf8")
    return PageHTML

def ReadListHTMLFromFilepath(Filepath):
    returnstring = ""
    with open(Filepath, encoding="utf8") as f:
        returnstring = f.read()
    PrintTextFile(Test_Output, returnstring, OverwritePrevious = True)
    return returnstring

def ParseHTML(PageHTML):
    ## Get the Effective Date (dd/mm/yy)
    EffectiveDateMatch = re.search("Effective from (?P<EffectiveFrom>\d{1,2}/\d{1,2}/\d{4})", PageHTML)
    EffectiveDateText = EffectiveDateMatch.group('EffectiveFrom').split('/')
    EffectiveDate = datetime.date(
        year = int(EffectiveDateText[2]), 
        month = int(EffectiveDateText[1]), 
        day = int(EffectiveDateText[0]))
    
    ## Cut out the table from the HTML and create an entry for each card on the list
    Card_Table = PageHTML[int(PageHTML.index("<tbody>") + len("<tbody>")):int(PageHTML.index("</tbody>"))].rstrip().split("</tr>")
    while('\n' in Card_Table): Card_Table.remove('\n')
    while('' in Card_Table): Card_Table.remove('')
    FL_List = []
    for Entry in Card_Table:
        EntryData = re.search("<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?" +
                              "<td.*?>(.*?)<\/td>.*?", Entry, re.MULTILINE|re.DOTALL)
        
        ## Make sure the entry obtains a full set of data
        if(EntryData is None):
            raise Exception("EntryData is None\nEntries done: " + str(len(FL_List)) + "\n")
        elif(len(EntryData.groups()) < 6):
            raise Exception("EntryData is too small")
        elif(EntryData.group(1) == '&nbsp;' or EntryData.group(1) == 'Card Type'):
            pass
        else:
            ## Replace '&nbsp;' with an empty string
            for g in EntryData.groups():
                g.replace('&nbsp;', '')
            
            ## Create the entry object
            FLE = FL_Entry()
            
            ## Type and Name
            FLE.Type = EntryData.group(1)
            FLE.Name = EntryData.group(2)
            
            ## Status, as integers
            if(EntryData.group(3) in Status_Enumerable): 
                FLE.Status_Advanced = Status_Enumerable.index(EntryData.group(3))
            else: FLE.Status_Advanced = 3
            if(EntryData.group(4) in Status_Enumerable): 
                FLE.Status_Traditional = Status_Enumerable.index(EntryData.group(4))
            else: FLE.Status_Traditional = 3
            
            ## Remarks column
            FLE.Remarks = EntryData.group(5)
            
            ## Href Link
            hrefLink = re.search('href="(?P<hrefLink>.*?)"', EntryData.group(6))
            try:
                FLE.Link = hrefLink.group('hrefLink')
            except:
                print("Exception occurred when retrieving the card's database link.\n" +
                      "Card: " + EntryData.group(1) + "\n" +
                      "HTML: " + EntryData.group(6) + "\n"
                      )
                break
            
            ## Append the new entry to the list
            FL_List.append(FL_Entry)

    ## Return the effective date and the list, cutting off the first entry
    return (EffectiveDate, FL_List)

ParseHTML(ReadListHTMLFromFilepath(Test_Page))
pass