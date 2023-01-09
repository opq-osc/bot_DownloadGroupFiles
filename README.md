# bot_DownloadGroupFiles
自动下载指定群的群文件


**botoy.json中需要添加的参数**

```
  {
  "autoDownloadGroupFiles.groups": [123456,654321],
  "autoDownloadGroupFiles.downloadPath": ""
  }
```
autoDownloadGroupFiles.groups 是监听的群号


autoDownloadGroupFiles.downloadPath 只能填绝对路径,不填的话就是默认路径,会下载在插件的files文件夹里
