import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filesize'
})
export class FileSizePipe implements PipeTransform {
  transform(size: number) {
    if (size / (1024 ** 3) > 1)
        return (size / (1024 ** 3)).toFixed(1) + ' GB';
    else if (size / (1024 ** 2) > 1)
        return (size / (1024 ** 2)).toFixed(1) + ' MB';
    else if (size / (1024) > 1)
        return (size / (1024)).toFixed(1) + ' KB';
    else
        return size + ' bytes'
  }
}