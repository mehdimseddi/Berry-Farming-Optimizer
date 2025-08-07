// frontend/lib/images.ts

const getImageUrl = (path: string) => {
    return `/images/${path}`;
};

export const ITEM_IMAGES = {
    // Berries (plants)
    leppa: getImageUrl("leppa.png"),
    cheri: getImageUrl("cheri.png"),
    pecha: getImageUrl("pecha.png"),
    strawbst: getImageUrl("rawst.png"),

    // Seeds (used for planting)
    plain_spicy: getImageUrl("plain_spicy.png"),
    very_spicy: getImageUrl("very_spicy.png"),
    very_bitter: getImageUrl("very_bitter.png"),
    plain_bitter: getImageUrl("plain_bitter.png"),
    very_sweet: getImageUrl("very_sweet.png"),
    plain_sweet: getImageUrl("plain_sweet.png"),
};