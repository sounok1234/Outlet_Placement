
## Files and Folders

* [json/studio_info.json](https://github.com/SocialConstruct/outlets/blob/master/json/studio_info.json) contains the coordinates in WCS for all the rooms, windows, and doors of this sample studio apartment. The coordinates are based on a [simplified floor plan](https://github.com/SocialConstruct/outlets/blob/master/png/studio_simple.png?raw=true). 
* [json/floor_info.json](https://github.com/SocialConstruct/outlets/blob/master/json/floor_info.json) contains the coordinates in WCS for all floors and pucks of the flooring system for this sample studio apartment.

Both files store coordinates in WCS and as **decimal inches** in the format of `(x,y)`.

The [/png](https://github.com/SocialConstruct/outlets/tree/master/png) folder contains reference images for this studio apartment, including a [possible final solution of outlet locations](https://github.com/SocialConstruct/outlets/blob/master/png/studio_with_outlets.png?raw=true). You can see the sample final solution including floors, supports, and outlet locations [here](https://github.com/SocialConstruct/outlets/blob/master/png/studio_final.png?raw=true)

## Rules of Outlet Placement
Here are basic rules of electrical outlet placement per the NEC rules:
* The maximum distance to a receptacle (outlet) along a wall is 6 feet (72 inches)
* A wall is defined as any space longer than 2 feet (24 inches)
    * Wall space includes the space measured around corners
    * The wall space continues unless broken by a doorway (aka, doors **do not** count towards the length of a wall segment)
    * The space occupied by windows counts as wall space (aka, windows **do** count towards the length of a wall segment)
* The following illustration may be helpful in visualizing the above rules:

![Another Rules Summary](https://www.naffainc.com/x/CB2/Elect/EImages/outletsneeded.gif)

### Other Rules
* For this example problem, kitchens do not count as wall space (they have their own set of rules, which are ignored for simplicity's sake)
* Bathrooms and closets can be ignored
* All windows in this floor plan have floor-to-ceiling glass. Therefore, outlets cannot be placed in front of them (even though they count as wall space)
* Outlets are 2" deep and 4" wide
* Outlets must go in-between pucks 
![Allowable Configuration](https://raw.githubusercontent.com/SocialConstruct/outlets/master/png/allowable_configuration.png)


