# Hero Grid GIFs

This directory contains the GIFs displayed in the hero grid on the homepage (`index.html`).

## Current GIFs

These 18 GIFs are currently being used, in order:

1. `ClutteredRetrieval2D.gif` - Displayed for ClutteredRetrieval2D
2. `Motion2D.gif` - Displayed for Motion2D
3. `Obstruction2D.gif` - Displayed for Obstruction2D
4. `PushPullHook2D.gif` - Displayed for PushPullHook2D
5. `DynObstruction2D.gif` - Displayed for DynObstruction2D
6. `ClutteredStorage2D.gif` - Displayed for ClutteredStorage2D
7. `DynPushPullHook2D.gif` - Displayed for DynPushPullHook2D
8. `DynPushT.gif` - Displayed for DynPushT
9. `DynScoopPour.gif` - Displayed for DynScoopPour
10. `StickButton2D.gif` - Displayed for StickButton2D
11. `Motion3D.gif` - Displayed for Motion3D
12. `Obstruction3D.gif` - Displayed for Obstruction3D
13. `Packing3D.gif` - Displayed for Packing3D
14. `TidyBot3D-ground.gif` - Displayed for TidyBot3D-ground
15. `TidyBot3D-table.gif` - Displayed for TidyBot3D-table
16. `TidyBot3D-cupboard.gif` - Displayed for TidyBot3D-cupboard
17. `TidyBot3D-base_motion.gif` - Displayed for TidyBot3D-base_motion
18. `RBY1A3D-cupboard.gif` - Displayed for RBY1A3D-cupboard

## How to Update

To change which GIF is displayed for a particular environment:

1. **Replace the GIF file** in this directory with your preferred GIF. Keep the same filename to maintain the connection.
   
   For example, if you want to use a different GIF for Motion2D, replace `Motion2D.gif` with your new GIF.

2. **After making changes**, the website will automatically use the new GIFs from this directory (once the code is updated to reference this folder instead of the original markdowns/assets paths).

## Original Sources

These GIFs were originally copied from:
- `markdowns/assets/demo_gifs/` - Contains demonstration GIFs organized by environment
- `markdowns/assets/random_action_gifs/` - Contains random action GIFs

You can browse these directories to find alternative GIFs for any environment.

## File Naming Convention

The filename should match the environment name exactly as it appears in the hero grid:
- For base environments: Use the base name (e.g., `Motion2D.gif`, `Obstruction2D.gif`)
- For variant-specific environments: Use the full variant name with hyphens (e.g., `TidyBot3D-ground.gif`)

## Notes

- All GIFs should be in `.gif` format
- Try to keep file sizes reasonable for web performance
- The GIFs are displayed in a grid layout on the homepage

