from PIL import Image, ImageResampling


def convert_jpeg_to_icon(jpeg_path,
                         icon_path,
                         sizes=[(32, 32), (64, 64), (128, 128), (256, 256)]):
    """  
    将JPEG图片转换为包含多个尺寸的ICO图标。  
      
    :param jpeg_path: JPEG图片的路径。  
    :param icon_path: 保存ICO图标的路径。  
    :param sizes: 图标尺寸的列表，格式为[(宽度, 高度), ...]。  
    """
    # 打开JPEG图片
    with Image.open(jpeg_path) as img:
        # 创建一个新的图像列表，每个图像都是原始图像的一个缩放版本
        images = [
            img.resize(size, resample=ImageResampling.LANCZOS)
            for size in sizes
        ]

        # 保存第一个图像作为ICO文件的主图像，并附加其他尺寸的图像
        images[0].save(
            icon_path,
            format='ICO',
            sizes=[img.size] + sizes[1:],
            append_images=[img.convert("RGBA") for img in images[1:]])


# 使用函数
jpeg_path = 'qq.jpeg'  # JPEG图片的路径
icon_path = 'new.ico'  # 保存ICO图标的路径
convert_jpeg_to_icon(jpeg_path, icon_path)
