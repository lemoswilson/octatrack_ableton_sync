# (WIP DO NOT USE IT)

# Octatrack Ableton Sync
Little workaround for the inability to set Octratrack’s `Chain After` setting to something like `Immediate`, that would allow it to behave the same way as `Direct Start` works on Analog Four. This scripted is intended to work on a very limited and specific set of configurations, I do not guarantee that this will work if you don't follow exactly what's been laid in this README file. Also, use this script at your own's risk.


## Motivation
The quickest response for changing patterns on Octatrack is `2/16` , which is definetely fine if you are performing and OT is the clock/master device on your setup. Things start to get a bit complicated if you want the OT to be a slave device, and you want to change patterns from devices other than the OT.  

This is where this script comes in. It’s inteded to allow you to write pattern changes to the OT from Ableton’s clips on Session view in a consistent and easy way. Albeit limited to work only on `4/4` time signature, and when Ableton’s `Clip Launch Quantization` setting is set to 1 bar, and Octatrack patterns are an integer number of bars long on a `4/4` time signature, it is enough for me to be able to write straightforward dance music without having to worry about syncing issues between both machines. 

With help from Ableton Drummer’s [MIDI NOTE TO BANK SUB PROGRAM](https://blog.abletondrummer.com/convert-midi-messages-in-ableton/), this script allows you to send Program Change messages on time from Session View Clips to Octatrack while keeping `Clip Launch Quantization` set to `1 bar`, so no more of that thing where Octatrack pattern chaining would be 1 bar behind your intention. 

NOTE: Before trying out this script, you might want to attempt sending `MIDI CC #35 (Stop/Start)` messages together with Program Changes messages. This could possibly allow you to instantly change patterns on the OT  without the need to worry about quantization issues, as long as you send the messages exactly at the moment you want it to change. For me, this setup did not work, hence the creation of this script. 
I do have the intention of writing a more generic version of this script that would allow a broader use case, but for now this is enough for my needs. PRs for generalizing the behavior for different `Clip Launch Quantization` and `Chain After` settings are welcome. 

## Installation
Clone/download the folder and add it to Ableton’s MIDI Remote Script path

- For Windows users `C:\ProgramData\Ableton\Live 11 <VERSION>\Resources\MIDI Remote Scripts`
- For macOS users:
    - Locate the Live application in Finder (typically `/Applications/`),
    - right click on it and select "Show Package Contents" in the context menu,
    - navigate to: `/Contents/App-Resources/MIDI Remote Scripts/`
- Launch Live and head back to `Preferences → Link MIDI → MIDI`
- Under the `Control Surface` section, choose an empty slot and assign `octatrack_ableton_sync`

## Ableton Project Setup
In order for this script to properly work, you need to have three MIDI tracks set up, and they should have the following names: `OT PCC`, `OT PCA`, and `OT IPCS`. You should write your MIDI notes on `OT PCC` track, and not touch`OT PCA` and `OT IPCS`. `OT PCC` track should be deactivated, and both `OT PCA` and `OT IPCS` should be activated and sending MIDI to your Octatrack Program Change IN channel. Live’s Global Launch Quantization set should be set to 1 bar. 

PCC Clip’s Start Marker and Loop Start should always be the same, and End Marker and Loop End should always be the same. If you want to increase the size of a loop, never do that by changing start points, but always the end.

## Octatrack Project Setup
`Chain After` should be set to `Pat Length`, and the patterns should follow the global `Chain After` settings.

## Terminology:
- Program Change Controller (PCC): The track we will write MIDI notes as Program Changes for the OT.
- Program Change Adjuster (PCA): The track that will have a time adjusted version of the clips in the PCC track.
- Immediate Program Change Sender (IPCS): The track that will send program changes to the OT when *triggering* clips on the PCC.

## Usage:
- Add the M4L device MIDI Notes to Program Change on the `OT PCC`, `OT PCA`, and `OT IPCS` tracks and set up it the way you like. Write MIDI Notes on Session View Clips on the PCC track, and **trigger them within the last bar before you want the pattern to change**.

### Notes
All clips on the PCC must have a note in the very beggining. Also, for this to work it requires that the notes in the PCC clips firing align correctly with the end of the playing pattern on OT. For example, if you add a note that will trigger a 4 bar pattern, the next note you add to the PCC clip should be after `4n bars` where `n` is an integer.