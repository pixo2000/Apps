import aspose.slides as slides

# Load presentation
pres = slides.Presentation("Glasfaserabend_Niedernhausen Ost  & West.pptx")

# Convert PPTX to PDF
pres.save("pptx-to-pdf.pdf", slides.export.SaveFormat.PDF)