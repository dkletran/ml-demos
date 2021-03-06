declare var require: any
let loadImage = require('blueimp-load-image');

function fixRotationOfFile(file) {
  return new Promise(resolve => {
    loadImage(file, img => {
      img.toBlob(blob => {
        resolve(blob);
      }, 'image/jpeg');
    }, {
      orientation: true,
      canvas: true
    });
  });
}

export async function fixRotation(arrayOfFiles) {
  for (let i = 0; i < arrayOfFiles.length; i++) {
    arrayOfFiles[i] = await fixRotationOfFile(arrayOfFiles[i]);
  }

  return arrayOfFiles;
};