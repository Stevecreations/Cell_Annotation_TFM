

## App description

Cell Dysplasia Annotation App enables the user to annotate microscopic images of blood cells. 
There are three main indicators pathologists use to detect whether a cell is dysplasic or not. These are:

**a)** Check for absence of granularity in the cell's cytoplasm. A healthy cell presents a certain granularity in the cytoplasm.

**b)** Check for Hyperchromasia. A dysplastic cell will display an increased chromatin content resulting in a deeply stained nuclei. 

**c)** Number of lobes of cell nuclei. A healthy cell usually present between 2 and 5 lobes.

Other factors to bear in mind are:

**d)** Ratio between the nuclei and the cytoplasm as Dysplastic cells present a larger nuclei than healthy ones

**e)** An increase of the Miotic figures.

![Healthy cell vs Dysplastic cell](/assets/images/healthy_vs_displastic.jpg)

This app allows the user to annotate and classify areas in an image. 
- Navigate the images in directory 
- Freehand draw, using the mouse to highlight specific areas of the image.
- Select annotation type Cytoplasm(Granular / Transparent), Chromatin (Heterogenic / Homogenic), Nº of Lobes (Hyposegmented/ Normal / Hypersegmented)
- Select the priority of each characteristic when deciding if a cell is Healthy or presents Dysplacia.
- Export the annotations made as a txt file (json format) and as an image.

## How to use this app
The first step is to update the path directoryehre the images are stores by clicking on `Update Image Path`. 

To annotate the image, first select the annotation label you want to apply: 

![Screenshot of label selector](/assets/images/select_label.jpg)

Then highlight the desired image area to annotate with the cursor:

![Screenshot of annotation](/assets/images/draw_annotation.jpg)

The width of the annotation brush can be changed with the slider bar `Width of annotation paintbrush` 

![Screenshot of width_paintbrush](/assets/images/width_paintbrush.jpg)

Additional annotations can be made by selecting a new label and highlighting the regions on the image.

![Screenshot of_additional_annotation](/assets/images/additional_annotation.jpg)

In order to classify the images correctly, it is important to select the decision criteria priority by clicking on the radio butons  `priority - 0(null) / 1(max) / 2 / 3(min)`

The user can also state if a cell is dysplactic or healthy by the redio button  `Cell condition`

![Screenshot of_Cell_condition](/assets/images/cell_condition.jpg)

To select a different image the press on the `previous` and `next`. The current annotations made on the image will be stored in a txt file in the same directory as the image source. An image with the annotations will also be stored will aso be stored .

![Screenshot of_Navigation](/assets/images/navigation.jpg)

To download an image with the annotations and/or info entered press on the check boxes `Save annotation` `Save_title` respectively

To erase an already made annotation click of the desired annotation and then hit the errase button on the top of the image editor.

![Erase_annotation](/assets/images/errase_annotation.jpg)



## Credits
S. Hernandez - 2021 **Universitat Politecnica de Catalunya** in collaboration with **Hospital Clinic de Barcelona**
