import { ImageIcon } from "@phosphor-icons/react";

const ImgPlaceholder =() => (
  <div
    className="
      upload-placeholder rounded-2
      h-100 w-100 d-flex align-items-center
      justify-content-center flex-column flex-fill
    "
    role="img"
    aria-label="No image selected"
  >
    <ImageIcon size={56} weight="fill" />
    <span className="mt-2 text-muted">No image selected</span>
  </div>
);

export default ImgPlaceholder;