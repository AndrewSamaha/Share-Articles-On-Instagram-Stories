function setImages(ogImage) {
    const img = document.getElementById('article-image')
    img.src = ogImage

    const storyContainer = document.getElementById('story-container')
    storyContainer.style.setProperty('--article-image', `url("${ogImage}")`)
}

function setFigCaption(title) {
    const figCaption = document.querySelector('figcaption')
    figCaption.innerText = title
}

function setText(text) {
    const textOverlay = document.getElementById('text-overlay')
    textOverlay.innerText = text
}

function setFontColor(fontColor) {
    const figCaption = document.querySelector('figcaption')
    if (figCaption) figCaption.style.color = fontColor;
    const textOverlay = document.querySelector('text-overlay');
    if (textOverlay) textOverlay.style.color = fontColor;
}