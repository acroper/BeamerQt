# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

FrameXML = ET.Element('Frame', id='frame_0')


TitleBar = ET.SubElement(FrameXML, 'TitleBar')
Titlebar_Visible = ET.SubElement(TitleBar, 'Visible', id='1')
Titlebar_Text = ET.SubElement(TitleBar, 'Content')

Titlebar_Visible.text = 'True'
Titlebar_Text.text = 'Contenido'




FrameXML2 = ET.Element('Frame', id='frame_1')


TitleBar2 = ET.SubElement(FrameXML2, 'TitleBar')
Titlebar_Visible2 = ET.SubElement(TitleBar2, 'Visible', id='2')
Titlebar_Text2 = ET.SubElement(TitleBar2, 'Content')

Titlebar_Visible2.text = 'True'
Titlebar_Text2.text = 'Contenido'



Documento = ET.Element('BeamerDoc')

Documento.append(FrameXML)
Documento.append(FrameXML2)



tree = ET.ElementTree(Documento)
ET.indent(tree, '  ')

tree.write("Test.xml", encoding="utf-8", xml_declaration=True)

print(tree)


