import tkinter.scrolledtext as tkscroll
import tkinter.messagebox as mb
import tkinter.filedialog as fd
import tkinter.font as font
import tkinter.dnd as dnd
import tkinter.commondialog as cd
import tkinter.dialog as dg
import tkinter.simpledialog as sd
import tkinter.ttk as ttk
import tkinter as tk

root = tk.Tk()
root.title("Mindustry Content Creator (or something idk)")
root.geometry("640x480")
root.minsize(320, 240)
root.maxsize(int(1366/1.5), int(768/1.5))

font = font.Font(root, font=("JetBrains Mono", 10, "roman"))

normal = 'normal'
disabled = 'disabled'

# test = tk.OptionMenu()


class Interface:

    def __init__(self):
        self.modes = ["Block", "Unit", "Item", "Liquid"]
        self.currentMode = "Block"
        self.blockAttributes = \
            {
                # General
                "health": "Health", "scaledHealth": "Scaled Health",
                "size": "Size", "offset": "Offset",
                "requirements": "Item requirements",
                "category": "Category",

                # Storage, crafter and item related
                "hasItems": "Has items", "hasLiquids": "Has liquids",
                "hasPower": "Has power", "outputsLiquid": "Outputs liquid",
                "consumesPower": "Consumes power",
                "outputsPower": "Outputs power",
                "connectedPower": "Power connectable",  # whether power nodes can connect
                "conductivePower": "Power conductor",  # whether conducts power
                "insulated": "Blocks power connections",
                "itemCapacity": "Item capacity",
                "dumpTime": "Item dump speed",
                "separateItemCapacity": "Separate item capacity",
                "liquidCapacity": "Liquid capacity",
                "liquidPressure": "Liquid pressure",  # liquid output speed
                "deconstructDropAllLiquid": "Drop liquids on deconstruct",
                "outputFacing": "Output facing",  # whether output to facing direction
                "noSideBlend": "Input from sides",  # whether input to accept from sides
                "displayFlow": "Display flow rate",
                "unloadable": "Unloadable",
                "isDuct": "Is duct",
                "ambientSound": "Ambient sound",
                "ambientSoundVolume": "Ambient volume",
                "buildTime": "Build time",
                "BuildVisibility": "Build visibility",
                "buildCostMultiplier": "Build cost multiplier",

                # Destroyable
                "destructible": "Destructible", "armor": "Armor",
                "baseExplosiveness": "Base explosiveness",
                "explosivenessScale": "Explosiveness scale",
                "drawCracks": "Draw cracks", "createRubble": "Create rubble",
                "crushDamageMultiplier": "Crush damage multiplier",

                # Units
                "unitCapModifier": "Unit cap modifier",
                "targetable": "Targetable", "suppressable": "Suppressable",
                "allowResupply": "Allow unit resupply",
                "absorbLasers": "Absorbs lasers",
                "canPickup": "Unit Pick-up-able",
                "updateInUnits": "Update in unit payload",
                "alwaysUpdateInUnits": "Force update in unit payload",

                # Misc 1
                "fillsTile": "Fills tile", "forceDark": "Force dark",
                "alwaysReplace": "Always replaceable",
                "replaceable": "Replaceable",
                "canOverdrive": "Overdriveable",
                "enableDrawStatus": "Draw status",
                "drawDisabled": "Draw disabled status",
                "conveyorPlacement": "Conveyor placement",
                "allowDiagonal": "Allow diagonal placement",
                "swapDiagonalPlacement": "Swap Diagonal Placement",
                "quickRotate": "Rotatable after placement",
                "allowDerelictRepair": "Allow derelict repair",

                # Misc 2
                "inEditor": "Visible in editor",
                "solid": "Is solid",
                "solidifes": "Can be solid",
                "teamPassable": "Non-solid to team",
                "underBullets": "Under Bullets",
                "rotate": "Rotatable",
                "variants": "Variants",
                "drawArrow": "Draw rotation arrow",
                "drawTeamOverlay": "Draw team overlay",
                "breakable": "Breakable",
                "unitMoveBreakable": "Unit move breakable",
                "rebuildable": "Rebuildable",
                "requiresWater": "Only water placement",
                "placeableLiquid": "Anywhere liquid placement",
                "placeablePlayer": "Player placeable",
                "squareSprite": "Full square sprite",
                "albedo": "Reflectiveness",
                "emitLight": "Emits light",
                "lightRadius": "Light emit radius",
                "fogRadius": "Fog uncover radius",
                "researchCostMultiplier": "Research cost multiplier",

                # Floors
                "placeableOn": "Can be placed on",
                "itemDrop": "Item drop",
                "playerUnmineable": "Player unmineable",

            }
        self.blockAttributeTypes = \
            [
                "input", "input",
                "input", "input",
                "input",
                "dropdown",

                "checkbox", "checkbox",
                "checkbox", "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "input",
                "input",
                "checkbox",
                "input",
                "input",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "input",
                "input",
                "input",
                "dropdown",
                "input",

                "checkbox", "input",
                "input",
                "input",
                "checkbox", "checkbox",
                "input",

                "input",
                "checkbox", "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",

                "checkbox", "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",

                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "input",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "checkbox",
                "input",
                "checkbox",
                "input",
                "input",
                "input",

                "checkbox",
                "input",
                "checkbox",
            ]
        self.buildVisibilities = \
            {
                "shown": "Shown",
                "hidden": "Hidden",
                "debugOnly": "Debug only",
                "editorOnly": "Editor only",
                "coreZoneOnly": "Core zone only",
                "worldProcessorOnly": "World processor only",
                "sandboxOnly": "Sandbox only",
                "campaignOnly": "Campaign only",
                "legacyLaunchPadOnly": "Legacy launch pad only",
                "notLegacyLaunchPadOnly": "Not legacy launch pad only",
                "lightingOnly": "Lighting only",
                "ammoOnly": "Ammo only",
                "fogOnly": "Fog only",
            }
        self.buildCategories = \
            {
                "turret": "Offensive",
                "production": "Production",
                "distribution": "Distribution",
                "liquid": "Liquid",
                "power": "Power",
                "defense": "Defense",
                "crafting": "Crafting",
                "units": "Unit-related",
                "effect": "Effects",
                "logic": "Logic",
            }
        self.blockAttributesKeys = list(self.blockAttributes)
        self.interface = []
    def construct(self):
        ttk.Button(root, text="destroy", command=self.destroy()).pack()
        for element in range(len(self.blockAttributes)):

            # Booleans
            if self.blockAttributeTypes[element] == "checkbox":
                self.interface.append(
                    ttk.Checkbutton(root, name=self.blockAttributesKeys[element],
                                    text=self.blockAttributes[self.blockAttributesKeys[element]],
                                    state="on",
                                    )
                )

            # Various inputs
            if self.blockAttributeTypes[element] == "input":
                self.interface.append(
                    ttk.Label(root, name=(self.blockAttributesKeys[element] + "Label"),
                              text=self.blockAttributes[self.blockAttributesKeys[element]],
                              ),
                )
                self.interface.append(
                    ttk.Entry(root, name=self.blockAttributesKeys[element],
                              )
                )

            # Dropdowns, there are only 2 of
            if self.blockAttributeTypes[element] == "dropdown":
                if self.blockAttributesKeys[element] == "category":
                    self.interface.append(
                        ttk.Label(root, name=(self.blockAttributesKeys[element] + "Label"),
                                  text=self.blockAttributes[self.blockAttributesKeys[element]],
                                  ),
                    )
                    self.interface.append(
                        ttk.Combobox(self.interface[element-1], name=(self.blockAttributesKeys[element]),
                                     values=[self.buildCategories[list(self.buildCategories)[_]]
                                             for _ in range(len(self.buildCategories))]
                                     )
                    )
                elif self.blockAttributesKeys[element] == "buildVisibility":
                    self.interface.append(
                        ttk.Label(root, name=(self.blockAttributesKeys[element] + "Label"),
                                  text=self.blockAttributes[self.blockAttributesKeys[element]],
                                  )
                    )
                    self.interface.append(
                        ttk.Combobox(self.interface[element-1], name=(self.blockAttributesKeys[element]),
                                     values=[self.buildVisibilities[list(self.buildVisibilities)[_]]
                                             for _ in range(len(self.buildVisibilities))]
                                     ).pack()
                    )
        for part in range(len(self.interface)):
            try:
                #self.interface[part].config(justify="center")
                ...
            except Exception as e:
                print(f"failed to configure {self.interface[part]}: {e}")
        for part in range(len(self.interface)):
            try:
                self.interface[part].pack()#fill=tk.X)
            except Exception as e:
                print(f"failed to pack {self.interface[part]}: {e}")
                tk.Label(text="broek").pack()
        print(self.interface)

    def destroy(self):
        print("begin destroyment")
        for part in range(len(self.interface)):
            try:
                self.interface[part].destroy()
            except Exception as e:
                print(f"failed to destroy {self.interface[part]}: {e}")

    def get_attributes_amount(self):
        return len(self.blockAttributes)

    def get_attributes(self):
        return self.blockAttributes

    def get_attributes_type(self):
        return self.blockAttributeTypes


# attrs = list(Interface().get_attributes())
# attrsT = Interface().get_attributes_type()
# attrsA = Interface().get_attributes_amount()
#
# for i in range(attrsA):
#     print(f"{attrs[i]}: {attrsT[i]}")

Interface().construct()

root.mainloop()