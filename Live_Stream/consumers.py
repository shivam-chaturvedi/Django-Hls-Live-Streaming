from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
import subprocess
import time
import os
import subprocess


# this class is for reciving blobs and creating live streaming hls segments and also updates master.m3u8
class HlsStreaming:

    def __init__(self): 
        self.TARGET_DURATION=4 # SET TARGET_DURATION ACCORDING TO YOUR VIDEO BLOBS COMING RATE FROM FRONTEND
        self.hls_dir_name=f'HLS_SEGMENTS_{time.strftime("%H_%M_%S")}'
        if not os.path.exists(self.hls_dir_name):
            os.mkdir(self.hls_dir_name)
        else:
            pass
            # raise Exception(self.hls_dir_name+" already exists!")

        lines=["#EXTM3U",
            "#EXT-X-VERSION:3",
            f"#EXT-X-TARGETDURATION:{self.TARGET_DURATION}",
            "#EXT-X-MEDIA-SEQUENCE:0",
            "#EXT-X-ALLOW-CACHE:NO"]
        if(os.path.exists("master.m3u8")):
            return None
        with open(("master.m3u8"),'w') as master:
            for line in lines:
                master.write(line)
                master.write("\n")

    async def convert_to_hls(self,video_data):
        try:
            timestamp=int(time.time())
            ffmpeg_command = [
                'ffmpeg',
                '-i', 'pipe:0',  # Read input from stdin (pipe)
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-f', 'hls',
                '-g','10',
                '-hls_time', f"{self.TARGET_DURATION}",  # Use the segment duration from above
                '-hls_list_size', '1',
                '-hls_segment_filename',
                os.path.join(self.hls_dir_name,f'segment_{timestamp}_%d.ts'),
                '-start_number', '0',
                '-y',
                '-hide_banner',
                '-loglevel',
                'error',
                '-nostats',
                os.path.join(self.hls_dir_name,'output.m3u8'),
            ]
            process=subprocess.run(ffmpeg_command,input=video_data)
            if(process.returncode==0):
                print("success")
                await self.update_master()
            else:
                print(process.stderr)
        except Exception as e:
            print(str(e))


    async def update_master(self):
        i=0
        with open(os.path.join(self.hls_dir_name,"output.m3u8"),'r') as output:
            lines=output.readlines()
        with open("master.m3u8", 'a') as master:
            for line in lines: 
                i += 1
                if i<= 4 or i == len(lines):
                    continue
                else:
                    if not line.startswith("#"):
                        master.write(f"{self.hls_dir_name}/"+line)
                    else:
                        master.write(line)
            master.write("\n")
            master.write("#EXT-X-DISCONTINUITY") 
            master.write("\n")

    async def stop_stream(self):
        try:
            with open("master.m3u8",'a') as master:
                master.write("\n")
                master.write("#EXT-X-ENDLIST")
                os.rename("master.m3u8",f"master_{self.hls_dir_name}.m3u8")
        except Exception as e:
            print(str(e))



class LiveStreamConsumer(AsyncConsumer,HlsStreaming):
    async def websocket_connect(self,event):
        await self.send({
            'type':'websocket.accept',
        })

    async def websocket_receive(self,event):
        data=event['bytes']
        await self.convert_to_hls(data)
        
    async def websocket_disconnect(self,event):
        await self.stop_stream()
        raise StopConsumer()
    





