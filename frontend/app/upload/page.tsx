import { UploadFlow } from "@/components/UploadFlow";
export default function UploadPage() {
return (
<div className="container mx-auto px-6 py-24 flex-grow flex flex-col justify-center">
<div className="max-w-2xl mx-auto w-full mb-12">
<h1 className="text-3xl font-medium text-text-primary mb-4">New Analysis</h1>
<p className="text-text-secondary">
Upload footage for comprehensive forensic detection. Processing occurs entirely locally.
</p>
</div>
<UploadFlow />
</div>
);
}
