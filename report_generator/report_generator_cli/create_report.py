"""Create Report.

Application to create pdf report based on parameters passed into it

@Params:
        data_source         - Data source for report creation
        report_name         - Title of the report and the file name
        report_author       - Author of the report
        university_name     - Name of the university
        university_school   - Name of the university school

@Todo:
    - Implement detect data source type to allow for differing file types/sources?
    - Error handling
    - Remove hardcoded elements
    - Split functions further or into their own file
    - Refactor the create_x_section functions into one function that takes a section arg
    - Add a font loader
    - add a font specification

"""


import os
import sys
import time
from pathlib import Path

import pandas
from fpdf import FPDF, TextMode
from loguru import logger

from report_generator.report_generator_cli.amphibian import AmphibianData

# Create report

DIR_PATH = (Path(os.path.dirname(os.path.realpath(__file__)))).parent


def create_report(
    data_source: str,
    report_name: str,
    report_author: str,
    university_name: str,
    university_school: str,
) -> None:
    """Create Report.

    Primary function that creates pdf object, sets fonts, calls
    component creation methods and saves output.

    Args:
        data_source         - Data source for report creation
        report_name         - Title of the report and the file name
        report_author       - Author of the report
        university_name     - Name of the university
        university_school   - Name of the university school

    """
    startTime = time.time()
    logger.debug(f"Create Report Started: {report_name}")

    curtime = time.time()
    logger.debug("Started reading data source")
    ds = read_data_source(data_source)
    logger.debug(f"Finished reading data source: {round(time.time() - curtime, 2)}s")

    pdf = FPDF()
    curtime = time.time()
    logger.debug("Started adding fonts")
    pdf.add_font(
        "OpenSans", fname=f"{DIR_PATH}/fonts/OpenSans-VariableFont_wdth,wght.ttf"
    )
    pdf.add_font(
        "OpenSansBold", fname=f"{DIR_PATH}/fonts/static/OpenSans/OpenSans-Bold.ttf"
    )
    logger.debug(f"Finished adding fonts: {round(time.time() - curtime,2)}s")

    curtime = time.time()
    logger.debug("Started creating title page")
    pdf = create_title_page(
        report_name, report_author, university_name, university_school, pdf
    )
    logger.debug("Finished creating title page: {round(time.time() - curtime, 2)}s")

    curtime = time.time()
    logger.debug("Started creating contents pages")
    pdf = create_contents_page(pdf, ds)
    logger.debug(
        f"Finished creating contents pages: {round(time.time() - curtime, 2)}s"
    )

    curtime = time.time()

    logger.debug("Started creating report pages")

    pdf = create_report_order_sections(ds, pdf)
    pdf.output(f"{'_'.join(report_name.split(' '))}.pdf")

    logger.debug(f"Finished creating report pages: {round(time.time() - curtime, 2)}s")

    fp = os.getcwd() + "/" + "_".join(report_name.split(" ")) + ".pdf"
    fs = round(os.path.getsize(fp / (1 << 20), 2))

    debug_mess = f"Create Report Finished: {report_name} - "
    debug_mess += f"Time Taken: {round((time.time() - startTime), 2)}s"
    debug_mess += ", File Size: "
    debug_mess += f"{round(os.path.getsize(fs))}MB"

    logger.debug(debug_mess)


# create title page


def create_title_page(
    report_name: str,
    report_author: str,
    university_name: str,
    university_school: str,
    pdf: object,
) -> object:
    """Create title page.

    Creates a title page based upon passed args. Adds text and images
    to pdf.page() then returns pdf object.

    Process:
        Adds page
        Designates contents section
        Adds background image
        Adds banner image
        Adds Text
        Returns pdf obj

    Args:
        data_source         - Data source for report creation
        report_name         - Title of the report and the file name
        report_author       - Author of the report
        university_name     - Name of the university
        university_school   - Name of the university school

    Return:
        pdf(obj) - pdf object

    """
    pdf = FPDF()
    pdf.add_page()
    pdf.start_section(name="Title Page", level=0)
    with pdf.local_context(fill_opacity=0.5, stroke_opacity=0.5):
        pdf.image(f"{DIR_PATH}/images/back.png", x=0, y=0, h=300)
    pdf.image(f"{DIR_PATH}/images/school_banner.png", x=30, y=250, h=50)
    with pdf.local_context(
        text_mode=TextMode.FILL, text_color=(227, 6, 19), line_width=2
    ):
        pdf.add_font(
            "OpenSans", fname=f"{DIR_PATH}/fonts/OpenSans-VariableFont_wdth,wght.ttf"
        )
        pdf.add_font(
            "OpenSansBold", fname=f"{DIR_PATH}/fonts/static/OpenSans/OpenSans-Bold.ttf"
        )
        pdf.set_font("OpenSansBold", "", 56)

        pdf.set_draw_color(255, 255, 255)
        pdf.ln(30)
        # pdf.write(20, report_name)
        pdf.cell(w=20)
        pdf.multi_cell(w=150, txt=report_name, align="L", border=0)
        pdf.ln(85)
        pdf.set_font("OpenSansBold", "", 28)
        # pdf.write(10, report_author)
        pdf.cell(w=20)
        pdf.cell(w=150, txt=report_author, align="L", border=0)
        pdf.set_font("OpenSans", "", 22)

        pdf.ln(20)
        # pdf.write(10, university_name)
        pdf.cell(w=20)
        pdf.cell(w=150, txt=university_name, align="L", border=0)

        pdf.ln(10)
        # pdf.write(10, university_school)
        pdf.cell(w=20)
        pdf.cell(w=150, txt=university_school, align="L", border=0)

    return pdf


# Contents page


def create_contents_page(pdf: object, data_frame: object) -> object:
    """Create contents page.

    Creates space for contents to be created in the document. Currently hardcoded.
    Will throw exception if the space isn't the correct amount.

    53 on first contents page
    63 every page after

    Args:
        pdf - pdf object

    Return:
        pdf - pdf object

    """
    num_of_pages = calc_number_of_contents_pages(data_frame)
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.start_section(name="Table Of Contents", level=0)
    pdf.insert_toc_placeholder(render_toc, num_of_pages)
    return pdf


def calc_number_of_contents_pages(data_frame: object) -> int:
    """Calc number of contents pages.

    Works out the number of contents pages required for
    pdf.insert_to_placeholder(render_toc, num_of_pages)

    Currently hardcoded.

    Formula used currently:
        53 on first contents page
        63 every page after

    Args:
        data_frame: Pandas DataFrame object

    Returns:
        count: integer of count

    """
    order_len = len((data_frame["Order"]).value_counts())
    family_len = len((data_frame["Family"]).value_counts())
    genus_len = len((data_frame["Genus"]).value_counts())

    total = order_len + family_len + genus_len

    additional_count = 0
    if ((total - 53) % 63) != 0:
        additional_count += 1

    count = 1 + ((total - 53) // 63) + additional_count

    return count


def create_report_order_sections(ds: object, pdf: object) -> object:
    """Create report order sections.

    Filter function that splits the data frame (ds) into smaller dataframes
    based on the 'Order' column in the dataframe.

    Process:
        Creates dataframe subsections
        Sorts the new dataframes.
        Loops through each of smaller dataframes to create contents section and level
        Writes section title
        Passes section to the next filter function.

    Args:
        ds - Pandas Dataframe object
        pdf - pdf object

    Returns:
        pdf - pdf object

    """
    order = ds["Order"]
    order_names = order.value_counts().index.tolist()
    order_names.sort()
    for name in order_names:
        sect = ds[ds["Order"] == name]
        pdf.add_page()
        pdf.start_section(name=name, level=0)
        pdf.set_font("OpenSansBold", "", 48)
        pdf.ln(20)
        pdf.write(30, f"Order: {name}", "C")
        pdf.ln(20)
        pdf = create_report_family_sections(sect, pdf)

    return pdf


def create_report_family_sections(section_list: object, pdf: object) -> object:
    """Create report family sections.

    Filter function that splits the data frame (section_list)
    into smaller dataframes based on the 'Family' column in the dataframe.

    Process:
        Creates dataframe subsections
        Sorts the new dataframes.
        Loops through each of smaller dataframes to create contents section and level
        Writes section title
        Passes section to the next filter function.

    Args:
        section_list - Pandas Dataframe object
        pdf - pdf object

    Returns:
        pdf - pdf object

    """
    family = section_list["Family"]
    family_names = family.value_counts().index.tolist()
    family_names.sort()
    for name in family_names:
        sect = section_list[section_list["Family"] == name]
        pdf.start_section(name=name, level=1)
        pdf.set_font("OpenSansBold", "", 36)
        pdf.ln(20)
        pdf.write(10, f"Family: {name}", "C")
        pdf.add_page()
        pdf = create_report_genus_sections(sect, pdf)

    return pdf


def create_report_genus_sections(section_list: object, pdf: object) -> object:
    """Create report genus sections.

    Filter function that splits the data frame (ds) into smaller dataframes
    based on the 'Family' column in the dataframe.

    Process:
        Creates dataframe subsections
        Sorts the new dataframes.
        Loops through each of smaller dataframes to create contents section
        and level
        Writes section title
        Passes section to the create report pages function.

    Args:
        section_list - Pandas Dataframe object
        pdf - pdf object

    Returns:
        pdf - pdf object

    """
    genus = section_list["Genus"]
    genus_names = genus.value_counts().index.tolist()
    genus_names.sort()
    for name in genus_names:
        sect = section_list[section_list["Genus"] == name]
        pdf.set_font("OpenSansBold", "", 36)
        pdf.write(10, f"Genus: {name}")
        pdf.start_section(name=name, level=2)
        pdf.ln(10)
        pdf = create_report_section_pages(sect, pdf)

    return pdf


# Create pages
def create_report_section_pages(section, pdf):
    """Create report section pages.

    Takes the section passed to it. Passes section to 'create_amphibian_list'
    function to get the data transformed into a list of amphibian objects. Sorts
    the list by name. Loops through list of amphibian objects and passes them to the
    'create_report_section_page' function.

    Args:
        section - pandas dataframe object
        pdf - pdf object

    Return:
        pdf - pdf object

    """
    amp_list = create_amphibian_list(section)
    amp_list = sorted(amp_list, key=lambda a: a.species)

    # Hardcoded example image will have to replace this
    amp_list[0].image_url_male = f"{DIR_PATH}/images/f1.jpg"
    amp_list[0].image_url_female = f"{DIR_PATH}/images/f2.jpg"

    report_style = "compact"

    for i in range(len(amp_list)):
        # pdf = create_report_section_page(amp, pdf)
        amp = amp_list[i]
        # Check if compact report
        if report_style == "compact":
            if i == 0 or i == 1 or i == 2:
                image_offset = 10
            else:
                image_offset = 0

            if (i + 1) % 3 == 0:
                image_offset += 165
                pdf = create_report_page_compact(amp, pdf, image_offset)
                pdf.add_page()
            elif i % 2 == 0:
                pdf = create_report_page_compact(amp, pdf, image_offset)
                if (i + 1) == len(amp_list):
                    pdf.add_page()
            else:
                image_offset += 85
                pdf = create_report_page_compact(amp, pdf, image_offset)
                if (i + 1) == len(amp_list):
                    pdf.add_page()
    return pdf


# create page
def create_report_section_page(amp, pdf):
    """Create report section page.

    Takes an instance of Amphibian and creates a page. Adds title.
    Adds images (insert_species_images). Adds data table (create_report_page_table).
    Then returns pdf object.

    Args:
        amp - Amphibian object
        pdf - pdf object

    Return:
        pdf - pdf object

    """
    pdf.start_section(name=amp.get_short_name(), level=3)
    pdf.set_font("OpenSansBold", "", 24)
    pdf.ln(20)
    pdf.write(10, amp.get_short_name())
    pdf = insert_species_images(amp, pdf)
    pdf = create_report_page_table(amp, pdf)
    pdf.add_page()

    return pdf


# add images


def insert_species_images(amp, pdf):
    """Insert species images.

    Takes an instance of Amphibian and pdf. Adds images (insert_species_images)
    to current pdf page. Then returns pdf object.

    FUNCTION CURRENTLY HARDCODED IMAGE VALUES

    Args:
        amp - Amphibian object
        pdf - pdf object

    Return:
        pdf - pdf object

    """
    WIDTH = 210
    pdf.ln(20)
    pdf.set_font("OpenSansBold", "", 16)
    pdf.write(5, "Species Images:")
    pdf.ln(75)
    if amp.has_image_url():
        pdf.image(f"{amp.image_url_male}", x=10, y=70, w=(WIDTH / 2) - 25, h=50)
        pdf.image(
            f"{amp.image_url_female}", x=WIDTH / 2, y=70, w=(WIDTH / 2) - 25, h=50
        )
        tcell_width = 60
        tcell_height = 5
        pdf.set_font("OpenSansBold", "", 10)
        pdf.cell(tcell_width, tcell_height, "Male Image", align="C", border=0)
        pdf.cell(tcell_width - 20, tcell_height)
        pdf.cell(tcell_width, tcell_height, "Female Image", align="C", border=0)
    else:
        pdf.image(
            f"{DIR_PATH}/images/frogsil1.png", x=10, y=70, w=(WIDTH / 2) - 25, h=50
        )
        pdf.image(
            f"{DIR_PATH}/images/frogsil2.png",
            x=WIDTH / 2,
            y=70,
            w=(WIDTH / 2) - 25,
            h=50,
        )
        tcell_width = 60
        tcell_height = 5
        pdf.set_font("OpenSansBold", "", 10)
        pdf.cell(tcell_width, tcell_height, "Missing Male Image", align="C", border=0)
        pdf.cell(tcell_width - 20, tcell_height)
        pdf.cell(tcell_width, tcell_height, "Missing Female Image", align="C", border=0)

    return pdf


# create data table
def create_report_page_table(amphibian_data, pdf):
    """Create report page table.

    Takes an instance of Amphibian and pdf. Adds the data in object to current pdf page
    in tabular format. Then returns pdf object.

    Args:
        amp - Amphibian object
        pdf - pdf object

    Return:
        pdf - pdf object

    """
    pdf.ln(20)
    pdf.set_font("OpenSansBold", "", 16)
    pdf.write(5, "Species Data:")
    pdf.ln(10)
    tcell_width = 88
    tcell_height = 5

    pdf.set_font("OpenSansBold", "", 8)

    for key, value in amphibian_data.__dict__.items():
        if key not in ["position", "image_url_male", "image_url_female"]:
            key = " ".join(key.split("_")).upper()
            pdf.set_font("OpenSansBold", "", 8)
            pdf.cell(tcell_width, tcell_height, str(key), align="L", border=1)
            pdf.set_font("OpenSans", "", 8)
            pdf.cell(tcell_width, tcell_height, str(value), align="L", border=1)
            pdf.ln(tcell_height)

    return pdf


def create_report_page_compact(amp: object, pdf, image_offset) -> object:
    """Create report page compact.

    Creates a report page with a more compact style.
    Fits more entries on the page over standard version.

    Args:
        amp: Amphibian object
        pdf: Fpdf2 pdf object
        image_offset: offset values for image placement

    Returns:
        pdf: Fpdf2 pdf object

    """
    pdf.start_section(name=amp.get_short_name(), level=3)
    pdf.set_font("OpenSansBold", "", 16)
    pdf.ln(5)
    pdf.write(10, amp.get_short_name())
    pdf = insert_species_images_compact(amp, pdf, image_offset)
    pdf = create_report_page_table_compact(amp, pdf)

    return pdf


def create_report_page_table_compact(amphibian_data, pdf):
    """Create report page table compact.

    Takes an instance of Amphibian and pdf. Adds the data in object
    to current pdf page in tabular format. Then returns pdf object.

    Args:
        amp - Amphibian object
        pdf - pdf object

    Return:
        pdf - pdf object

    """
    pdf.ln(10)
    lcell_width = 35
    rcell_width = 65
    tcell_height = 4

    pdf.set_font("OpenSansBold", "", 8)

    for key, value in amphibian_data.__dict__.items():
        if key not in ["position", "image_url_male", "image_url_female"]:
            key = " ".join(key.split("_")).upper()
            pdf.set_font("OpenSansBold", "", 8)
            pdf.cell(lcell_width, tcell_height, str(key), align="L", border=1)
            pdf.set_font("OpenSans", "", 7)
            pdf.cell(rcell_width, tcell_height, str(value), align="L", border=1)
            pdf.ln(tcell_height)

    return pdf


def insert_species_images_compact(amp, pdf, image_offset):
    """Insert species images compact.

    Takes an instance of Amphibian and pdf. Adds images (insert_species_images)
    to current pdf page. Then returns pdf object.

    FUNCTION CURRENTLY HARDCODED IMAGE VALUES

    Args:
        amp - Amphibian object
        pdf - pdf object

    Return:
        pdf - pdf object

    """
    WIDTH = 210
    pdf.set_font("OpenSansBold", "", 16)
    if amp.has_image_url():
        pdf.image(
            f"{amp.image_url_male}",
            x=120,
            y=(25 + image_offset),
            w=(WIDTH / 3) - 25,
            h=30,
        )
        pdf.image(
            f"{os.getcwd()}/report_generator_cli/images/maletext.png",
            x=120,
            y=(55 + image_offset),
            h=5,
        )
        pdf.image(
            f"{amp.image_url_female}",
            x=120,
            y=(60 + image_offset),
            w=(WIDTH / 3) - 25,
            h=30,
        )
        pdf.image(
            f"{os.getcwd()}/report_generator_cli/images/femaleimage.png",
            x=120,
            y=(91 + image_offset),
            h=4,
        )
    else:
        pdf.image(
            f"{DIR_PATH}/images/frogsil1.png",
            x=120,
            y=(25 + image_offset),
            w=(WIDTH / 3) - 25,
            h=30,
        )
        pdf.image(
            f"{os.getcwd()}/report_generator_cli/images/maletext.png",
            x=120,
            y=(55 + image_offset),
            h=5,
        )
        pdf.image(
            f"{DIR_PATH}/images/frogsil2.png",
            x=120,
            y=(60 + image_offset),
            w=(WIDTH / 3) - 25,
            h=30,
        )
        pdf.image(
            f"{os.getcwd()}/report_generator_cli/images/femaleimage.png",
            x=120,
            y=(91 + image_offset),
            h=4,
        )

    return pdf


# create index
def create_report_index():
    """Create report index pages.

    Currently unimplemented.

    """


def read_data_source(file_name: str) -> object:
    """Read data source.

    Read the data_source file and transform it into a pandas dataframe

    Args:
        file_name - String path to file

    Returns:
        df - Pandas dataframe object

    """
    df = pandas.read_excel(file_name)
    df["comb_name"] = df["Order"] + " " + df["Family"]

    return df


def create_amphibian_list(data_section: object) -> list:
    """Create amphibian list.

    Takes a row of data from the dataframe and extracts values and instantiates
    an instance of the AmphibianData class

    Args:
        data_section - Pandas dataframe object

    Return:
        amphibian_list - list of amphibian objects

    """
    amphibian_list = []
    for row in data_section.iterrows():
        vals = []
        for value in row:
            if isinstance(value, int):
                vals.append(value)
            else:
                vals = [*vals, *value.values]
        for i in range(len(vals)):
            if pandas.isna(vals[i]):
                vals[i] = "Unknown"
            if vals[i] == "ND":
                vals[i] = "Unknown"
        a = AmphibianData(vals)
        amphibian_list.append(a)
    return amphibian_list


def render_toc(pdf, outline):
    """Render table of contents.

    Function to render table of contents - taken from example code of
    FPDF2 documentation

    53 on first contents, 63 after

    Args:
        pdf - pdf object
        outline - outline object

    """
    pdf.ln(20)
    pdf.set_font("Helvetica", size=24)
    pdf.underline = False
    pdf.write(5, "Table of contents:")
    pdf.underline = False
    pdf.ln(20)
    pdf.set_font("Courier", size=12)

    for section in outline:
        if section.level < 3:

            link = pdf.add_link()
            pdf.set_link(link, page=section.page_number)
            text = f'{" " * section.level * 2}{section.name}'
            text += f' {"." * (60 - section.level*2 - len(section.name))} '
            text += f"{section.page_number}"
            pdf.multi_cell(
                w=pdf.epw,
                h=pdf.font_size,
                txt=text,
                new_x="LMARGIN",
                new_y="NEXT",
                align="C",
                link=link,
            )


if __name__ == "__main__":

    args = sys.argv

    startTime = time.time()
    data_source = args[1]
    report_name = args[2].upper()
    report_author = args[3].upper()
    university_name = args[4].upper()
    university_school = args[5].upper()

    print(f"Creating Report: {report_name}.pdf")
    create_report(
        data_source, report_name, report_author, university_name, university_school
    )
    print(f"Report Complete: {report_name}.pdf")
    executionTime = time.time() - startTime
    print("Execution time in seconds: " + str(executionTime))