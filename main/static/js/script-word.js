document.getElementById('download-word').addEventListener('click', async () => {
    const title = document.querySelector('.title-input').value || 'Без названия';
    const editor = document.querySelector('.ql-editor');

    const children = [];

    for (const el of editor.querySelectorAll(':scope > *')) {

        const paragraphChildren = [];

        for (const node of el.childNodes) {

            if (node.nodeType === Node.TEXT_NODE) {
                paragraphChildren.push(
                    new docx.TextRun({
                        text: node.textContent || ''
                    })
                );

                continue;
            }

            if (node.nodeType !== Node.ELEMENT_NODE) {
                continue;
            }

            const tag = node.tagName.toLowerCase();

            if (tag === 'img') {
                const image = await createImageRun(node);

                if (image) {
                    paragraphChildren.push(image);
                }

                continue;
            }

            const text = node.textContent || '';

            if (text) {
                paragraphChildren.push(
                    new docx.TextRun({
                        text: text,
                        bold:
                            tag === 'strong' ||
                            tag === 'b' ||
                            node.querySelector('strong, b') !== null,

                        italics:
                            tag === 'em' ||
                            tag === 'i' ||
                            node.querySelector('em, i') !== null,

                        underline:
                            tag === 'u' ||
                                node.querySelector('u') !== null
                                ? {}
                                : undefined,

                        strike:
                            tag === 's' ||
                            tag === 'strike' ||
                            node.querySelector('s, strike') !== null
                    })
                );
            }
        }

        children.push(
            new docx.Paragraph({
                children: paragraphChildren
            })
        );
    }

    if (children.length === 0) {
        children.push(
            new docx.Paragraph({
                children: [
                    new docx.TextRun('')
                ]
            })
        );
    }

    const doc = new docx.Document({
        sections: [{
            children
        }]
    });

    const blob = await docx.Packer.toBlob(doc);

    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `${title}.docx`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(() => {
        URL.revokeObjectURL(url);
    }, 1000);
});

async function createImageRun(img) {
    const src = img.getAttribute('src');

    if (!src) {
        return null;
    }

    try {
        const response = await fetch(src);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const buffer = await response.arrayBuffer();

        const contentType =
            response.headers.get('content-type') || '';

        let type = 'png';

        if (
            contentType.includes('jpeg') ||
            contentType.includes('jpg')
        ) {
            type = 'jpg';
        } else if (
            contentType.includes('gif')
        ) {
            type = 'gif';
        }

        let width =
            parseInt(img.getAttribute('width')) ||
            img.naturalWidth ||
            600;

        let height =
            parseInt(img.getAttribute('height')) ||
            img.naturalHeight ||
            400;

        const maxWidth = 600;

        if (width > maxWidth) {
            const scale = maxWidth / width;

            width = Math.round(width * scale);
            height = Math.round(height * scale);
        }

        return new docx.ImageRun({
            type: type,

            data: new Uint8Array(buffer),

            transformation: {
                width: width,
                height: height
            }
        });

    } catch (error) {
        console.error(
            'Не удалось добавить картинку в Word:',
            src,
            error
        );

        return null;
    }
}