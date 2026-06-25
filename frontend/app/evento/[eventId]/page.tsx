import ZvZConsole from '@/components/ZvZConsole';

export const dynamic = 'force-dynamic';

export default async function EventCheckinPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = await params;
  return (
    <ZvZConsole
      apiBaseUrl={process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'}
      initialEventId={eventId}
      initialView="checkin"
    />
  );
}
