import os
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
from xml.dom import minidom
from datetime import datetime
import re

def prettify(element):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    pretty_xml = pretty_xml.replace('&lt;br/&gt;', '<br/>')

    return pretty_xml

def extract_title_and_author(title_line):
    """Extract title and author from the title line, cleaning numbering and whitespace."""
    # Remove any leading numbering and excess whitespace from the title
    cleaned_title = re.sub(r"^\s*\d+[.,)]?\s*|\s*\d+,\s*|\s*[A-Z][.,)]\s*", "", title_line)
    # Extract title and optional author
    match = re.match(r"Title: (.+?)(?: \((.*?)\))?$", cleaned_title)
    if match:
        title = match.group(1).strip()
        author = match.group(2).strip() if match.group(2) else " "
        return title, author
    return cleaned_title.strip(), " "  # Fallback

def convert_text_to_openlyrics_xml(input_text, output_xml_path):
    lines = input_text.split('\n', 1)
    title_line = lines[0]
    title, author = extract_title_and_author(title_line)

    song = Element('song', {
        'xmlns': "http://openlyrics.info/namespace/2009/song",
        'version': "0.8",
        'createdIn': "OpenLP 3.0.2",
        'modifiedIn': "OpenLP 3.0.2",
        'modifiedDate': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    })

    properties = SubElement(song, 'properties')
    titles = SubElement(properties, 'titles')
    title_elem = SubElement(titles, 'title')
    title_elem.text = title

    authors = SubElement(properties, 'authors')
    author_elem = SubElement(authors, 'author')
    author_elem.text = author

    lyrics = SubElement(song, 'lyrics')
    verses = input_text.split('\n\n')[1:]  # Skip the title line

    for i, verse_text in enumerate(verses, start=1):
        verse_text = verse_text.strip()
        if not verse_text:  # Skip empty verses
            continue
        verse = SubElement(lyrics, 'verse', name=f"v{i}")
        lines = SubElement(verse, 'lines')
        # Ensure line breaks are correctly formatted and unnecessary whitespace is removed
        lines_text = verse_text.replace('\n', '<br/>').strip()
        lines_text = verse_text.replace('\u2028', '<br/>').strip()
        lines.text = re.sub(r'\s*<br/>\s*', '<br/>', lines_text)  # Remove whitespace around <br/>

    xml_str = prettify(song)

    # Write to the output XML file
    with open(output_xml_path, 'w', encoding='utf-8') as file:
        file.write(xml_str)

# Example usage
input_dir = 'input'
output_dir = 'output'

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.xml')

        with open(input_path, 'r', encoding='utf-8') as file:
            input_text = file.read()

        convert_text_to_openlyrics_xml(input_text, output_path)
