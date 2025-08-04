import os
import zipfile
import tarfile
from pathlib import Path
from typing import Union, Literal


def compress_path_advanced(source_path: Union[str, Path],
                           output_dir: Union[str, Path],
                           archive_name: str = None,
                           format_type: Literal['zip', 'tar', 'tar.gz', 'tar.bz2'] = 'zip') -> str:
    """
    压缩文件或目录为指定格式

    Args:
        source_path: 要压缩的文件或目录路径
        output_dir: 压缩包保存目录
        archive_name: 压缩包名称（可选）
        format_type: 压缩格式 ('zip', 'tar', 'tar.gz', 'tar.bz2')

    Returns:
        str: 压缩包的完整路径
    """
    source_path = Path(source_path)
    output_dir = Path(output_dir)

    if not source_path.exists():
        raise FileNotFoundError(f"源路径不存在: {source_path}")

    if not output_dir.exists():
        raise FileNotFoundError(f"输出目录不存在: {output_dir}")

    # 生成压缩包名称和扩展名
    if archive_name is None:
        base_name = source_path.name
    else:
        base_name = archive_name

    if format_type == 'zip':
        archive_path = output_dir / f"{base_name}.zip"
        return _compress_zip(source_path, archive_path)
    elif format_type in ['tar', 'tar.gz', 'tar.bz2']:
        ext = '.tar' if format_type == 'tar' else f'.{format_type}'
        archive_path = output_dir / f"{base_name}{ext}"
        return _compress_tar(source_path, archive_path, format_type)
    else:
        raise ValueError(f"不支持的压缩格式: {format_type}")


def _compress_zip(source_path: Path, archive_path: Path) -> str:
    """ZIP格式压缩"""
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if source_path.is_file():
            zipf.write(source_path, source_path.name)
        else:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_path.parent)
                    zipf.write(file_path, arcname)
    return str(archive_path)


def _compress_tar(source_path: Path, archive_path: Path, format_type: str) -> str:
    """TAR格式压缩"""
    mode_map = {
        'tar': 'w',
        'tar.gz': 'w:gz',
        'tar.bz2': 'w:bz2'
    }

    with tarfile.open(archive_path, mode_map[format_type]) as tar:
        tar.add(source_path, arcname=source_path.name)

    return str(archive_path)


if __name__ == '__main__':
    source_path = 'D:/opt/inference-server'
    output_dir = 'D:/opt'
    archive_name = 'test'
    format_type = 'zip'
    compress_path_advanced(source_path, output_dir, archive_name, format_type)
