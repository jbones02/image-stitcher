import { Card, Button } from "react-bootstrap";
import { Download } from "react-bootstrap-icons";

const ResultCard = ({ resultUrl, anchorRef }) => {
  if (!resultUrl) return null;

  return (
    <Card
      className="shadow-lg rounded-4 p-2 px-sm-2 px-md-3 py-sm-3 dirty-white-bg borderless"
      style={{ "--gap-x": "1rem" }}
    >
      <Card.Body className="px-3 px-sm-4 px-md-4 pt-2 pb-3">
        <div className="text-start">
          <h2 className="mb-3 fs-2">Result</h2>
        </div>

        <img
          src={resultUrl}
          alt="Stitched result"
          className="img-fluid rounded mb-4"
        />

        <div className="d-flex justify-content-end">
          <a
            ref={anchorRef}
            href={resultUrl}
            download="stitched.jpg"
            className="text-decoration-none mb-0"
          >
            <Button
              className="d-flex justify-content-center align-items-center gap-2"
              size="lg"
            >
              <Download /> Download
            </Button>
          </a>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ResultCard;
