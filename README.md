# FFmpeg File Size Reducer GUI

I wanted a simple GUI for reducing MP4 file sizes, I've just been using this command

`ffmpeg -i input.mp4 -vcodec libx264 -crf 22 output.mp4`

I fed information to ChatGPT and did a little of tweaking myslef on the lines I understood.  You can adjust the constant rate factor from 18-25.  The features I included were:

  * Saving to a different file folder
  * Overwritting the original file
  * Slider for constant rate factor adjustment
