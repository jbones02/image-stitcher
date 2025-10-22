import { Card, Form } from "react-bootstrap";
import ImgPlaceholder from "./Placeholder.jsx";

const ImageUploadCard = ({
  title,
  controlId,
  onChange,
  src,
  accept = "image/*",
}) => {
  const hasImage = Boolean(src);

  return (
    <Card className="w-100 rounded-4">
      <div className="text-start">
        <h2 className="m-3 mb-2 fs-4">{title}</h2>
      </div>

      <Card.Body className="pt-0 px-3 pb-3">
        <Form.Group controlId={controlId} className="mb-3">
          <Form.Label className="visually-hidden">{title} file input</Form.Label>
          <Form.Control type="file" accept={accept} onChange={onChange} />
        </Form.Group>

        <div className="upload-preview-frame d-flex justify-content-center w-100">
          {hasImage ? (
            <img
              src={src}
              alt={`${title} preview`}
              className="rounded-2"
            />
          ) : (
            <ImgPlaceholder />
          )}
        </div>
      </Card.Body>
    </Card>
  );
};

export default ImageUploadCard;
