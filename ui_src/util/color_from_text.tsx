/*
 * Returns a random colour based on a provided text.
 * The mapping is deterministic, so the same text should
 * always return the same colour.
 */

export function colorFromText(text: string): Record<string, string>
{
    // Extract each character into an array and convert to a numeric character code
    let charCodes = text.split('').map((c) => (c.charCodeAt(0)))

    // Uses same hash concept as java string hashcode. I'm told this is fast and vaguely decent.
    let hash = charCodes.reduce((a: number, b: number): number => (
        (b << 5) - b + a
    ), 0x811c9dc5 /* random seed */)

    // Map this number into three R, G, B components
    let rgb = [0, 8, 16].map((i) => (
        (hash >> i) & 0xFF)
    );

    // Format colour
    let color = rgb.map((segment) => (
        ("00" + segment.toString(16)).substr(-2)
    ));

    // Format the inverse colour
    let inverse = rgb.map((segment) => (
        ("00" + (255 - segment).toString(16)).substr(-2)
    ));

    // Calculate a black-white text colour
    let averageColor = rgb.reduce((a, b) => (a + b), 0) / rgb.length;
    let bw = (averageColor > 0x90) ? "black" :
             (averageColor < 0x70) ? "white" :
             '#' + inverse.join('');

    // Return combined HEX string
    return {
        color: '#' + color.join(''),
        inverse: '#' + inverse.join(''),
        text: bw
    }
}
