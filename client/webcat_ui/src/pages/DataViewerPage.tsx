import { Stack, Container } from 'react-bootstrap';
import DataViewer from '../components/DataViewer';

function InteractiveParser() {
  return (
    <Container className="bg-none" >
        <Stack gap={3} >
            <DataViewer />
        </Stack>
    </Container>
  );
}

export default InteractiveParser;