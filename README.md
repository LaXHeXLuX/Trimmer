# Trimmer

## Introduction

Trimmer is an add-on for Blender. Its goal is to simplify the process of mapping an existing trim-sheet to a model. The basic workflow is: 

* Preliminary: creating a plane divided into faces that reference the positions of trims on the trim-sheet  
* Adding the trim locations to the add-on panel  
* Applying a trim to a selected face or faces  
* Rotating and reflecting the applied trim if necessary

## Installation

Download release 0.2.2 of Trimmer from [the github page](https://github.com/LaXHeXLuX/Trimmer/releases).  
In Blender 2.80 or later, go to *Edit → Preferences → Add-ons → Install from Disk*. Browse to the downloaded zip file, select it, and *Install from Disk*.  
The add-on can now be found in the add-ons list, where it can be enabled, disabled, or uninstalled.

## Preliminary work

Before using the add-on, a reference object to the trim-sheet must be created. In Blender, create a new Plane object.  
In Edit mode, divide the plane into rectangular faces so that each trim is covered by a face.  

The main techniques for the face subdivision are:

* Knife tool  
* Loop cuts  
* Edge subdivision

with the exact method left up to the user’s preference.  

Below are two examples of a trim-sheet and the respective face layout in Blender:

| ![Trim sheet 1](/pictures/preliminary/trimsheet1.png) | ![Trim sheet 1 divided](/pictures/preliminary/trimsheet1_divided.png) |
|:---:|:---:|
| *Trim-sheet 1: wood textures and iron decals* | *Trim-sheet 1 divided into faces* |

| ![Trim sheet 2](/pictures/preliminary/trimsheet2.png) | ![Trim sheet 2 divided](/pictures/preliminary/trimsheet2_divided.png) |
|:---:|:---:|
| *Trim-sheet 2: varying materials and signs* | *Trim-sheet 2 divided into faces* |

## Manual

### Panel location

After installing the add-on, a new Panel *Trimmer* appears in the 3D viewport sidebar. The sidebar can be opened by pressing N:  
| ![Panel location](/pictures/manual_usage/panel_location.png) |
|:---:|
| *A new panel named “Trimmer” visible in 3D viewport’s sidebar* |

### Setup Instructions

At first, the *Trimmer* panel only shows a single *Add trim* button, because no trims have been added to the add-on yet. To add trims, select a face from your trim-sheet plane and click *Add trim*. A new row appears in the panel:  
![Add trim](/pictures/manual_usage/add_trim.gif)  
Whenever you need to remove a trim, press the X button. After adding all trims, the panel will look similar to this:  
![Setup complete](/pictures/manual_usage/setup_complete.png)  
The add-on setup is now complete.

### Usage

Each trim can be applied to either *Fit* or *Fill* the trim texture:

* The *Fit* option will fit the selection inside the trim without stretching it:  
![Apply Fit](/pictures/manual_usage/apply_fit.gif)  
* The *Fill* option will stretch the selection to fill the trim:  
![Apply Fill](/pictures/manual_usage/apply_fill.gif)  

After applying a trim, options for *Mirror*, *Rotate*, and *Confirm* appear. When you're happy with the trim position, pressing *Confirm* will finalise it.

The *Mirror* button mirrors the applied selection across the Y-axis:
![Mirror](/pictures/manual_usage/mirror.gif)

The function of *Rotation* depends on the chosen fitting option: 

* Fit: *Rotation* is a slider that rotates the selection by a number of degrees
![Fit rotation](/pictures/manual_usage/rotate_fit.gif)
* Fill: *Rotation* is a button that rotates the selection shape edgewise
![Fill rotation](/pictures/manual_usage/rotate_fill.gif)

### Example

Let’s go through an example. I have a barrel model that I need to texture using a wood trim-sheet. I have kept the topology as simple as possible, making the final scaling adjustments after texturing to simplify the texturing process.   
![Example start](/pictures/example/example_start.png)

In the image above, the model and its default UV map can be seen.   
The Preliminary work (adding the trims into the addon) has been done beforehand.  
Depending on preference, the texturing may be done while in the *UV editing* view, or in the *Layout* view, without checking the UV Editor at all. To follow along easier, I will do it while in the *UV Editing* view.

First I will texture the bases of the barrel. Since those are circular with an arbitrary number of sides, I have to use the *Fit* option, and using *Fill* would yield the following error:  
![Example fill error](/pictures/example/example_fill_error.png)  
After using the *Fit* option, I rotate the face by 60 degrees, mirror, and confirm the placement:
![Example fit rotation mirror](/pictures/example/example_fit_rotate_mirror.gif)  
Next, I texture the sides. In order to correctly unwrap a loop of faces, an edge must be marked as a seam:   
![Example seam](/pictures/example/example_seam.png)  
Now, a loop of faces can be textured. In the below image I have textured all the side loops, alternating reclaimed wood (mirroring it in the center to avoid creating a pattern) and a black metallic bar:  
![Example texture continued](/pictures/example/example_texture_continued.png)  
Lastly, I make a single modeling adjustment, increasing the size of the barrel in the center to make it more authentic:  
![Example texture done](/pictures/example/example_texture_done.png)  
With this, the example texturing is complete.